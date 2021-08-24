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
channel = client.get_channel(cn.staff)
temp = []

def main():
    global df
    df = pd.read_csv('worldcities.csv', index_col=0)
    df = df.drop(columns=["iso2","iso3","capital","population","id"])
    global channel
    
if __name__ == '__main__':
    main()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    channel = client.get_channel(cn.staff)
    embedVar = discord.Embed(title="UoN CS Cities", description="Click on link to view interactive Map", url="https://00000111.co.uk/map.html")
    embedVar.set_thumbnail(url="https://00000111.co.uk/map.html")
    await channel.send(embed=embedVar)

def validStr(city, country):
    if(city != "" and city.isnumeric() == False and country != "" and country.isnumeric() == False):
        return True
    else:
        return False

def add(city, country):
    res = df.query("(city_ascii=='%s' | admin_name=='%s') & country=='%s'" % (city, city, country))
    return res

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel == client.get_channel(cn.staff) and  message.content.startswith('!add'):
        embedVar = discord.Embed(title="New Command to MaxMap", color=0xff0080)
        embedVar.set_author(name=(message.author.nick + " | " + message.author.name + message.author.discriminator), icon_url=message.author.avatar_url)
        embedVar.add_field(name="Message:", value=message.content, inline=False)
        embedVar.add_field(name="Time:", value=str(datetime.datetime.now()), inline=False)
        await client.get_channel(cn.spam).send(embed=embedVar)

    if message.content.startswith('!add'):
        global sended
        sended = message
        strip = message.content.replace("!add", "")
        if strip == "":
            await sended.channel.send("Please enter a city and country - For help do !maphelp")
        else:
            strip = strip.title()
            split = strip.split(',')
            if(len(split) == 1):
                await sended.channel.send("Please enter a city and country - For help do !maphelp")
            else:
                city = split[0]
                country = split[1]
                city = city.lstrip(" ")
                country = country.lstrip(" ")

                if(validStr(city, country)):
                    res = add(city, country)
                    if(res.empty):
                        await sended.channel.send((city + ", " + country + ' not found, check spelling - Or try English spelling.'))
                    else:
                        if(res.shape[1] > 1):
                            res = res.iloc[0]
                        try: 
                            mb.checkDataset(res, temp)
                            try:
                                ret = mb.addToDataset(res)
                                temp.append(ret)
                                await sended.channel.send("City Added to Map! - Give it a few minutes to update.")
                            except Exception as e:
                                await sended.channel.send(e)
                        except Exception as e:
                            await sended.channel.send(e)

    if message.content.startswith('!maphelp'):
        helpembed = discord.Embed(title="MaxMap Help", description="**Type in '!add', followed by your city (above 10,000 population), and the country it is in.** \n **For example:** !add Nottingham, United Kingdom. \n\n Please note, the dataset that I am using for Cities and Countries is public, and so it may not be up-to-date or politically correct.",color=0xff0080)
        helpembed.set_footer(text="If you are having issues message/mention @jozef")
        await message.channel.send(embed=helpembed)
        
    if message.content.startswith('!map'):
        embedVar = discord.Embed(title="UoN CS Cities", description="Click on link to view interactive Map", url="https://00000111.co.uk/map.html")
        embedVar.set_thumbnail(url="https://00000111.co.uk/map.html")
        await message.channel.send(embed=embedVar)

client.run(cn.DISCORD_BOT_TOKEN)
