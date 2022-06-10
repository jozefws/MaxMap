# -*- coding: utf-8 -*-

"""
Created on Sun Aug 15 23:21:49 2021
Updated on Fri Jun 10 01:31:49 2022
@author: jozef sieniawski
"""

import discord
import constants as cn
import mapbox as mb
import datetime;
from positionstack import ps_search

client = discord.Client()
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
    embedVar.set_author(name=(str(message.author.nick) + " | " + str(message.author.name) + str(message.author.discriminator)), icon_url=message.author.avatar_url)
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
    embedVar.add_field(name="Message:", value=str("Error:" + e), inline=False)
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
            ret = mb.addToDataset(res, message.author)
            temp.append(ret)
            #Send update to channel sent from
            await sended.channel.send("City/Town Added to Map! - Give it a few minutes to update.")
        except Exception as e:
            await message_error(str(e) + " Mapbox Dataset error", sended)
    except Exception as e:
            await message_error(str(e) + " Mapbox Dataset error", sended)   


if __name__ == '__main__':
    main()


client.run(cn.DISCORD_BOT_TOKEN)

