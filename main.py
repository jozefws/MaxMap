# -*- coding: utf-8 -*-

"""
Created on Sun Aug 15 23:21:49 2021
Updated on Fri Jun 10 01:31:49 2022
@author: jozef sieniawski
"""

import pkg_resources
pkg_resources.require("discord.py==2.0.0a4364+g1a903272")
import discord
from discord.ui import Select, View
import constants as cn
import mapbox as mb
import datetime;
from positionstack import ps_search
import traceback

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
temp = []


# Main function, sets disable global variable to false.
def main():
    global disable
    disable = False


# Logs when cleint is ready
@client.event
async def on_ready():
    print('{0.user} logged in.'.format(client))


# Message handler
@client.event
async def on_message(message):
    global disable

    # Ignore messages from self
    if message.author == client.user:
        return

    # Toggle handling
    if message.content == "!toggle" and message.author.id in cn.mods:
        await message_toggle(message)

    # If disabled, then ignore all other commands
    if disable == True:
        await message.channel.send("The bot is currently down.")
        return

    # Banned user handling
    if  message.content.startswith('!add') and message.author.id in cn.banned:
        await message.channel.send("You do not have sufficient permissions to do this.")
        return

    # Default add command handling
    if message.content.startswith('!add'):       
        #Send Log Message
        await message_log(message)
        await message_add(message)
        
    # Help command handling
    if message.content == '!maphelp':
        await message_help(message)
       
    # Map command handling
    if message.content == '!map':
        await message_map(message)

    # Delete user entry command handling
    if message.content == '!delete':
        await message_delete(message)



#Checks string size and value for query
def validStr(query):
    if(query != "" and query.isnumeric() == False):
        return True    
    else:
        return False


# Sets disable global variable to true/false and updates channel.
async def message_toggle(message):
    if disable == True:
            disable = False
            await message.channel.send("Map Re-enabled.")
    elif disable == False:
        disable = True
        await message.channel.send("Map Disabled.")


# Logs message to spam channel set in constants.py/cn.spam
async def message_log(message):
    embedVar = discord.Embed(title="New Command to MaxMap", color=0xff0080)
    embedVar.set_author(name=(str(message.author.nick) + " | " + str(message.author.name) + str(message.author.discriminator)), icon_url=message.author.display_avatar.url)
    embedVar.add_field(name="Message:", value=message.content, inline=False)
    embedVar.add_field(name="Time:", value=str(datetime.datetime.now()), inline=False)
    await client.get_channel(cn.spam).send(embed=embedVar)


# Sends embeded message to relevant channel containing URL to map
async def message_map(message):
    embedVar = discord.Embed(title="UoN CS Cities", description="Click on link to view interactive Map", url="https://precursor.cs.nott.ac.uk/map.html")
    embedVar.set_thumbnail(url="https://precursor.cs.nott.ac.uk/map.html")
    await message.channel.send(embed=embedVar)


# Sends embeded message to relevant channel with bot usage instruction
async def message_help(message):
    helpembed = discord.Embed(title="MaxMap Help", description="**Type in '!add', followed by your city/town and the country it is in for more accuracy.** \n **For example:** !add Nottingham, United Kingdom. \n\n Please note, the dataset may not be up-to-date or politically correct.",color=0xff0080)
    helpembed.set_footer(text="If you are having issues message/mention @jozef")
    await message.channel.send(embed=helpembed)


# Error message handling, sends default error to user but detailed error to spam channel
async def message_error(e, sended):
    await sended.channel.send("An error has occured and has been logged, give me a chance to look what happened lol.")
    embedVar = discord.Embed(title="MaxMap ERROR", color=0xf56342)
    embedVar.add_field(name="Message:", value=str("Error: " + e + " " + str(traceback.format_exc())), inline=False)
    await client.get_channel(cn.spam).send(embed=embedVar)


# Main functionaliy. Adds user city to map.
async def message_add(message):
    global sended
    sended = message
    strip = message.content.replace("!add", "")

    # Check if string is null
    if strip == "":
        await sended.channel.send("Please enter a city and country - For help do !maphelp")
        return
    
    #Title text
    strip = strip.title()

    # Check if string is valid
    if (validStr(strip) == False):
        await sended.channel.send("Invalid Search Query, please only use UTF-8 characters and include no numbers.")
        return
    try:
        # Search for city usiong positionstack API
        res = ps_search(strip)
    except Exception as e:
        message_error(e, sended)
        return

    try: 
        #Check dataset with current city, pass through temp array too
        ret = mb.checkDataset(res, temp)
        if type(ret) is dict:
            if(len(ret) > 1):
                temp.append(ret)
                if mb.countUpdate(ret['ref'], temp, message.author):
                    await sended.channel.send("Your city is already in the list so it has been added to the counter!\n")
                    return
            if(len(ret) == 1):
                if mb.countUpdate(ret['ref'], temp, message.author):
                    for i in temp:
                        if ret['ref'] == i['ref']:
                            i['tempcount'] = str(int(i['tempcount']) + 1)
                await sended.channel.send("Your city is already in the list so it has been added to the counter!\n")
                return
        try:
            #Append the return value to temp
            ret = mb.addToDataset(res, message.author, strip)
            temp.append(ret)
            #Send update to channel sent from
            await sended.channel.send("City/Town Added to Map! - Give it a few minutes to update.")
        except Exception as e:
            await message_error(str(e) + " Mapbox Dataset error 1a", sended)
    except Exception as e:
            await message_error(str(e) + " Mapbox Dataset error 1b", sended)   

async def message_delete(message):
    global sended
    sended = message
    res = ""
    try:
        res = mb.userList(str(message.author))
    except Exception as e:
        await message_error(str(e) + " Mapbox Dataset error 2a", sended)
        return
    
    if res == None or res == [] or res == "":
        await sended.channel.send("You have no cities in the list. (message_delete 1)")
        return

    await message_delete_select(res, message)

async def message_delete_select(res, message):
    if res == None or res == [] or res == "":
        await message.channel.send("You do not have any cities in the list. (message_delete 2)")
        return
    view = View()
    select = Select(placeholder="Hi, "+ str(message.author) +",  Select a city to delete:", max_values=1)
    for feature in res:
        if feature['properties']['Title'] == "":
            title = "Unknown"
        else:
            title = feature['properties']['Title']

        select.add_option(label = title, value = feature['id'])

    async def entry_delete(interaction):
        if interaction.response.is_done():
            return
        try:
            mb.updateFeatureNames(str(interaction.user), select.values[0])
            await interaction.response.send_message("City/Town Deleted from Map!")
        except Exception as e:
            await message_error(str(e) + " Mapbox Dataset error 2b", sended)
            return

    select.callback = entry_delete
    
    view.add_item(select)
    await sended.channel.send("Please select a city from the list to remove - There may be a delay between deletion and the request being propagated to the map.", view=view)
    return True








if __name__ == '__main__':
    main()


client.run(cn.DISCORD_BOT_TOKEN)

