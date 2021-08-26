# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 23:21:49 2021

@author: jozef sieniawski
"""
import discord
import constants as cn
import pandas as pd
import mapbox as mb
import datetime;


client = discord.Client()
temp = []

def main():
    global df
    df = pd.read_csv('worldcities.csv', index_col=0)
    df = df.drop(columns=["iso2","iso3","capital","population","id"])
    
if __name__ == '__main__':
    main()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!add'):

        #Send Log Message
        embedVar = discord.Embed(title="New Command to MaxMap", color=0xff0080)
        embedVar.set_author(name=(message.author.nick + " | " + message.author.name + message.author.discriminator), icon_url=message.author.avatar_url)
        embedVar.add_field(name="Message:", value=message.content, inline=False)
        embedVar.add_field(name="Time:", value=str(datetime.datetime.now()), inline=False)
        await client.get_channel(cn.spam).send(embed=embedVar)

        #Process String
        global sended
        sended = message
        strip = message.content.replace("!add", "")
        if strip == "":
            await sended.channel.send("Please enter a city and country - For help do !maphelp")
        else:
            #Title text and split into list based on comma delim
            strip = strip.title()
            split = strip.split(',')
            #Checks if only one is entered, needs both.
            if(len(split) == 1 or split[1] == ""):
                await sended.channel.send("Please enter a city and country - For help do !maphelp")
            else:
                #Removes any extra spacing
                city = split[0].lstrip(" ")
                country = split[1].lstrip(" ")

                #Further checks.
                if(validStr(city, country)):
                    #Fetch City from spreadsheet, if empty error, if more than one choose first.
                    res = add(city, country)
                    if(res.empty):
                        await sended.channel.send((city + ", " + country + ' not found, check spelling - Try without symbols, ASCII characters only.'))
                    else:
                        if(res.shape[1] > 1):
                            res = res.iloc[0]
                        try: 
                            #Check dataset with current city, pass through temp array too
                            mb.checkDataset(res, temp)
                            try:
                                #Append the return value to temp
                                ret = mb.addToDataset(res)
                                temp.append(ret)
                                #Send update to channel sent from
                                await sended.channel.send("City/Town Added to Map! - Give it a few minutes to update.")
                            except Exception as e:
                                await sended.channel.send(e)
                        except Exception as e:
                            await sended.channel.send(e)

    #Extra Commands
    if message.content == '!maphelp':
        helpembed = discord.Embed(title="MaxMap Help", description="**Type in '!add', followed by your city/town (above 10,000 population), and the country it is in.** \n **For example:** !add Nottingham, United Kingdom. \n\n Please note, the dataset that I am using for Cities and Countries is public, and so it may not be up-to-date or politically correct.",color=0xff0080)
        helpembed.set_footer(text="If you are having issues message/mention @jozef")
        await message.channel.send(embed=helpembed)
        
    if message.content == '!map':
        embedVar = discord.Embed(title="UoN CS Cities", description="Click on link to view interactive Map", url="http://www.cs.nott.ac.uk/~pszmw/MaxMap/Web/map.html")
        embedVar.set_thumbnail(url="http://www.cs.nott.ac.uk/~pszmw/MaxMap/Web/map.html")
        await message.channel.send(embed=embedVar)

    if message.content == '!reece' and message.channel == client.get_channel(cn.mentor):
        await message.channel.send("https://cdn.discordapp.com/attachments/859436872597897257/880154423958061127/reece.png")
    
#Checks string size and value for both city and country
def validStr(city, country):
    if(city != "" and city.isnumeric() == False and country != "" and country.isnumeric() == False):
        return True
    else:
        return False

#Check DF based on a few columns and return result
def add(city, country):
    res = df.query("(city_ascii=='%s' | admin_name=='%s') & country=='%s'" % (city, city, country))
    return res

   
client.run(cn.DISCORD_BOT_TOKEN)
