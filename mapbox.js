// Require the necessary discord.js classes
const { Client, GatewayIntentBits, EmbedBuilder} = require('discord.js');

const { token } = require('./config.json');
// Create a new client instance
const client = new Client({ intents: [GatewayIntentBits.Guilds] });

// When the client is ready, run this code (only once)
client.once('ready', () => {
    console.log('\nONLINE - MaxMaP is awake and ready to add some markers!\n');
});

client.on('interactionCreate', async interaction => {
	if (!interaction.isChatInputCommand()) return;

	const { commandName } = interaction;

	if (commandName === 'addcity') {
        await interaction.reply({ embeds: [ addCity() ] });
    } else if (commandName === 'deletecity') {
        await interaction.reply({ embeds: [ deleteCity() ] });
	} else if (commandName === 'map') {
		await interaction.reply('https://precursor.cs.nott.ac.uk/map.html');
	}else if(commandName === 'info'){
        await interaction.reply({ embeds: [ infoEmbed() ] });
    }
});

function infoEmbed() {
    return infoEmbed = new EmbedBuilder()
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

}


// Login to Discord with your client's token
client.login(token);


