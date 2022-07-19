#!/usr/bin/env python3

'''
This script calculates the ratio of messages sent per user in a channel to the total number of
messages in the server.
'''

import discord
from discord.ext import commands

#####

IGNORE = [] # Put channels to ignore here
MAX_DEPTH = 1000000 # Maximum depth to search for messages

#####

# Retireves the bot token
with open('token.txt', 'r') as file:
    TOKEN = file.read().rstrip()

# Set permissions for the bot
INTENTS = discord.Intents.default()
INTENTS.members = True

# Initialize the bot
BOT = commands.Bot(command_prefix="?", intents=INTENTS)

@BOT.command()
async def member_msg_ratio(ctx):
    '''Get all members in the server and their message ratio'''

    member_msg_count = {} # Storage for messages and chars per member

    # Iterate through servers
    for guild in BOT.guilds:
        await ctx.send(f'[!] This may take a *very* long time!')

        member_count = len([member for member in guild.members if not member.BOT])
        active_member_count = 0
        total_msg_count = 0
        total_char_count = 0

        # Populate dictionary with members
        for member in guild.members:
            if not member.BOT:
                member_msg_count[str(member)] = [0, 0]

        # Iterate through channels
        for channel in ctx.guild.channels:
            # Only text channels are considered (obviously)
            if isinstance(channel, discord.TextChannel) and str(channel) not in IGNORE:

                # Iterate over all messages in the channel (up to MAX_DEPTH)
                async for message in channel.history(limit=MAX_DEPTH):
                    if not message.author.BOT: # Exclude bot messages
                        msg_len = len(message.content)
                        try:
                            member_msg_count[str(message.author)][0] += 1
                            member_msg_count[str(message.author)][1] += msg_len
                        except KeyError: # If member not in dictionary, add them (user likely left)
                            member_msg_count[str(message.author)] = [1, msg_len]
                    total_msg_count += 1
                    total_char_count += msg_len
                    active_member_count += 1

                    # Print progress (debug)
                    print(f'[!] At message {total_msg_count}, char {total_char_count}')

        # Write data to CSV file for storage and parsing
        csv = 'Member,Messages,Chars,AvgCharsPerMessage\n'
        for key in member_msg_count:
            csv += f'{key},{member_msg_count[key][0]},{member_msg_count[key][1]},'
            if member_msg_count[key][0]:
                csv += f'{round(int(member_msg_count[key][1]) / int(member_msg_count[key][0]))}\n'
            else:
                csv += f'0\n'
        with open('MessagesByMember.csv', 'w') as csv_file:
            csv_file.write(csv)

        # Report string
        report = f'**[!] Analysis complete!**\nStats:\n'
        report += f' - {total_msg_count} messages were reviewed.\n'
        report += f' - {total_char_count} chars were reviewed.\n'
        report += f' - {member_count} members were reviewed.\n'
        report += f' - Participating members average '
        report += f'{round(total_char_count / active_member_count)} characters per message\n'
        report += f' - Ignored channels: #{" #".join(IGNORE)}.\n'

        await ctx.send(report)
        await ctx.send(file=discord.File(r'MessagesByMember.csv'))

###############################################################################

# Connectivity check
@BOT.command()
async def hello(ctx):
    '''Connectivity test (use this to check if the bot is reachable)'''

    await ctx.send('Hello')

# Start the bot
BOT.run(TOKEN)
