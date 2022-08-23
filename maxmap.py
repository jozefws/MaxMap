import discord
from discord import option
import constants as cn
import embeds as emb
import databasefunctions as dbf
import positionstackfunctions as psf
import maxboxfunctions as mbf
description = """
MaxMap is a bot :)
"""
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = discord.Bot(intents=intents, description=description)

@bot.slash_command(description = "Add your city to the community map! **WARNING - Enter your nearest CITY, not town/village**")
@discord.commands.option("city", description="Enter your city, e.g. Nottingham")
@discord.commands.option("country", description="Enter your country, e.g. England")
async def addcity(ctx: discord.ApplicationContext, city: str, country: str):

    # Cheks is data is numeric, if so return error
    if((city.isnumeric() == True) or (country.isnumeric() == True or country == "" or city == "")):
        await ctx.send_response(embed=emb.error("Please enter a valid city and country."), ephemeral=True)
        return
    
    # Checks if city is longer than 25 characters, if so return error
    if(len(city) > 25):
        await ctx.send_response(embed=emb.error("Please enter a city less than 25 characters. Unless you live in one of these: https://www.worldatlas.com/articles/the-10-longest-place-names-in-the-world.html, then thats cool - ping me @jozef#0111"), ephemeral=True)
        return

    # Checks if country is longer than 25 characters, if so return error
    if(len(country) > 25):
        await ctx.send_response(embed=emb.error("Please enter a country less than 25 characters. If this is a problem please ping me @jozef#0111."), ephemeral=True)
        return

    # Checks if user has already added a city to the map, if so return error
    status, message = dbf.user_already_added(ctx.author.id)
    if(status == True):
        await ctx.send_response(embed=emb.error("You already have an entry in the map, please delete it first!"), ephemeral=True)
        return

    # Converts the city and country to coordinates
    lat, lng = psf.city_country_to_coords(city, country)
    if(lat == False or lng == False):
        print("city_country_to_coords ERROR " + message)
        await ctx.send_response(embed=emb.error("There was an error with fetching your city, it is being looked into. ERR_AC_1"), ephemeral=True)
        return

    # Checks if the city is already in the map, if so increment the counter
    status, mapboxid = dbf.already_added(lat, lng)
    if(status == True):
        await IncrementCityFunc(ctx, lat, lng, mapboxid)
    else:

        # ADD TO DATABASES AND MAPBOX
        status, featureID = mbf.add_entry(lat, lng, (str(ctx.author.name) + "#"+ str(ctx.author.discriminator)))
        if(status == False):
            await ctx.send_response(embed=emb.error("There was an error with adding your city to the map, it is being looked into. ERR_AE_1 " + str(featureID)), ephemeral=True)
            print("add_entry ERROR " + message)
            return

        status, mapboxid = dbf.add_city_to_mapboxdb(city, country, lat, lng, featureID)
        if(status == False):
            await ctx.send_response(embed=emb.error("There was an error with adding your city to the map, it is being looked into. ERR_AE_2 " + str(mapboxid)), ephemeral=True)
            print("add_city_to_mapboxdb ERROR " + message)
            return

        status, message = dbf.add_city_to_maxmapdb(ctx.author.id, (str(ctx.author.name) + "#"+ str(ctx.author.discriminator)), mapboxid)
        if(status == False):
            print("add_city_to_maxmapdb ERROR " + message)
            await ctx.send_response(embed=emb.error("There was an error with adding your city to the map, it is being looked into. ERR_AE_3 " + str(message)), ephemeral=True)
        else:
            await ctx.send_response(embed=emb.success("Your city has been added to the map! Wait for the map to be updated, see it by using **/map**"), ephemeral=True)
        return


@bot.slash_command(description = "See the community map!")
async def map(ctx: discord.ApplicationContext):
    await ctx.send_response("https://precursor.cs.nott.ac.uk/map.html")


@bot.slash_command(description = "Delete your entry from the map")
async def deletecity(ctx: discord.ApplicationContext):
    status, message = dbf.user_already_added(ctx.author.id)
    if(status == False):
        await ctx.send_response(embed=emb.error("You don't have an entry in the map, please add one first! Or an error occurred: " + str(message)), ephemeral=True)
        return
    else:
        status, mapboxID = dbf.delete_city_from_maxmapdb(ctx.author.id)
        if(status == False):
            await ctx.send_response(embed=emb.error("There was an error with deleting your city from the map, it is being looked into. ERR_DC_1 " + str(mapboxID)), ephemeral=True)
            print("delete_city_from_maxmapdb ERROR " + mapboxID)
            return

        status, getFeatureID, deleted = dbf.decrement_city(mapboxID)
        if(status == False):
            await ctx.send_response(embed=emb.error("There was an error with deleting your city from the map, it is being looked into. ERR_DC_2 " + str(getFeatureID)), ephemeral=True)
            print("decrement_city ERROR " + getFeatureID)
            return
        
        if(deleted == True):
            status, message = mbf.delete_feature(getFeatureID)
            if(status == False):
                await ctx.send_response(embed=emb.error("There was an error with deleting your city from the map, it is being looked into. ERR_DC_3 " + str(message)), ephemeral=True)
                print("delete_entry ERROR " + message)
                return
            else:
                await ctx.send_response(embed=emb.success("Your city has been deleted from the map! Wait for the map to be updated, see it by using **/map**"), ephemeral=True)

        else:
            status, count, names = dbf.get_names_and_count(getFeatureID)
            if(status == False):
                await ctx.send_response(embed=emb.error("There was an error with fetching your city, it is being looked into. ERR_DC_4"), ephemeral=True)
                print("get_names_and_count ERROR " + count)
                return

            status, lat, lng = dbf.get_lat_lng(getFeatureID)
            if(status == False):
                await ctx.send_response(embed=emb.error("There was an error with fetching your city, it is being looked into. ERR_DC_5"), ephemeral=True)
                print("get_lat_lng ERROR " + lat)
                return

            status, message = mbf.update_entry(getFeatureID, float(lat), float(lng), names, count)
            if(status == False):
                await ctx.send_response(embed=emb.error("There was an error with deleting your city from the map, it is being looked into. ERR_DC_6 " + str(message)), ephemeral=True)
                print("update_entry ERROR " + message)
                return
            else:
                await ctx.send_response(embed=emb.success("Your entry has been deleted from the map! Wait for the map to be updated, see it by using **/map**"), ephemeral=True)
            return

@bot.slash_command(description = "Get information about maxmap")
async def info(ctx: discord.ApplicationContext):
    await ctx.send_response(embed = emb.info, ephemeral=True,)

async def IncrementCityFunc(ctx, lat, lng, mapboxid):
    # Gets the featureID of the mapbox feature based on lat and lng stored in Database
    status, getFeatureID = dbf.get_feature_id(mapboxid)
    if(status == False):
        await ctx.send_response(embed=emb.error("There was an error with fetching your city, it is being looked into. ERR_IC_1"), ephemeral=True)
        print("get_feature_id ERROR " + message)
        return
        
    status, message = dbf.add_city_to_maxmapdb(ctx.author.id, (str(ctx.author.name) + "#"+ str(ctx.author.discriminator)), mapboxid)
    if(status == False):
        await ctx.send_response(embed=emb.error("There was an error with incrementing your city, it is being looked into. ERR_IC_2"), ephemeral=True)
        print("INCREMENT CITY ERROR " + message)
        return
    
    # Add one to the count
    status, message = dbf.increment_city(lat, lng)
    if(status == False):
        await ctx.send_response(embed=emb.error("There was an error with incrementing your city, it is being looked into. ERR_IC_3"), ephemeral=True)
        print("INCREMENT CITY ERROR " + message)
        return

    # Gets the discord usernames associated with the featureID and the number of them.
    status, count, names = dbf.get_names_and_count(getFeatureID)
    if(status == False):
        await ctx.send_response(embed=emb.error("There was an error with fetching your city, it is being looked into. ERR_IC_4"), ephemeral=True)
        print("get_names_and_count ERROR " + count)
        return
    
    # Update the count and names on mapbox
    status, message = mbf.update_entry(getFeatureID, lat, lng, names, count)
    if(status == False):
        await ctx.send_response(embed=emb.error("There was an error incrementing the count, it is being looked into. ERR_IC_5"), ephemeral=True)
        print("get_feature_id ERROR " + message)
        return  
    await ctx.send_response(embed=emb.success("This city is already in the map, incremented the counter!"), ephemeral=True)
    return

bot.run(cn.DISCORD_BOT_TOKEN)
