const { SlashCommandBuilder, Routes } = require('discord.js');
const { REST } = require('@discordjs/rest');
const { clientId, guildId, token } = require('./config.json');

const commands = [
	new SlashCommandBuilder().setName('addcity').setDescription('Add your city to MapMax!'),
	new SlashCommandBuilder().setName('deletecity').setDescription('Delete your MapMax entry.'),
	new SlashCommandBuilder().setName('map').setDescription('Get a link to the map.'),
    new SlashCommandBuilder().setName('info').setDescription('MapMax Information.'),
]
	.map(command => command.toJSON());

const rest = new REST({ version: '10' }).setToken(token);

rest.put(Routes.applicationGuildCommands(clientId, guildId), { body: commands })
	.then(() => console.log('Successfully registered application commands.'))
	.catch(console.error);
