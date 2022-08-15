const { EmbedBuilder, MessageActionRow, MessageButton } = require('discord.js');

const infoEmbed = new EmbedBuilder()
    .setDescription('MaxMaP is a bot that allows you to add and delete cities to a community map!')
    .setColor('0x9704bb')
    .setFields(
        {
            name: 'Adding to the map',
            value: 'Use the /addcity command with your city and country, e.g. Nottingham, England',
        },
        {
            name: 'Remove from the map',
            value: 'Use the /deletecity command',
        },
        {
            name: 'To see the map',
            value: 'Use the /map command and follow the link'
        })
    .setFooter({text:'Any issues contact @jozef#0111 :)'});