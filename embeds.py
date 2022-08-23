import discord
info = discord.Embed(
    title="MaxMap Information",
    type="rich",
    description="MaxMap is a bot that allows you to add your city to the community map.",
    color=discord.Colour(0x9704bb),
) 
info.add_field(name= 'Adding to the map',value='Use the /addcity command with your city and country, e.g. Nottingham, England', inline=False)
info.add_field(name= 'Viewing the map',value='Use the /map command to view the map', inline=False)
info.add_field(name= 'Deleting from the map',value='Use the /deletecity command to delete your entry from the map', inline=False)
info.set_footer(text='Please note that this map is publically available - Any issues contact @jozef#0111 :)')

def error(msg):
    error = discord.Embed(
        title="MaxMap Error",
        type="rich",
        description=msg,
        color=discord.Colour(0x9704bb),
    )
    return error

def success(msg):
    error = discord.Embed(
        title="MaxMap",
        type="rich",
        description=msg,
        color=discord.Colour(0x9704bb),
    )
    return error