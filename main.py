# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 23:21:49 2021

@author: jozef sieniawski
"""
import discord
import constants
import pandas as pd
import mapbox as mb

client = discord.Client()
channel = client.get_channel(876594408638783518)

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
    channel = client.get_channel(876594408638783518)
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

    if message.content.startswith('!add'):
        global sended
        sended = message
        message = message.content.strip("!add")
        split = message.split(',')
        city = split[0]
        country = split[1]
        city = city.lstrip()
        country = country.lstrip()
       
        if(validStr(city, country)):
            res = add(city, country)
            if(res.empty):
                await sended.channel.send((city + ", " + country + ' not found, check spelling - Or try English spelling.'))
            else:
                if(res.shape[1] > 1):
                    res = res.iloc[0]
                print(res)
                try: 
                    mb.checkDataset(res)
                    try:
                        mb.addToDataset(res)
                        await sended.channel.send("City Added to Map!")
                    except Exception as e:
                        await sended.channel.send(e)
                except Exception as e:
                    await sended.channel.send(e)
                    
client.run(constants.DISCORD_BOT_TOKEN)