import discord
import datetime
import pytz

guild_to_log_channel_map = {
    354836976492347394: 354836976949788674,  # SassTest
    100781489800609792: 673315310752890929,  # Sassy Squad
}

with open('BotSecret.txt', 'r+') as auth_file:
    bot_secret = auth_file.readline()

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


def was_deaf_or_mute_change(before_state, after_state):
    deafened_or_muted = False
    if before_state.deaf != after_state.deaf:
        deafened_or_muted = True
    elif before_state.mute != after_state.mute:
        deafened_or_muted = True
    elif before_state.self_mute != after_state.self_mute:
        deafened_or_muted = True
    elif before_state.self_deaf != after_state.self_deaf:
        deafened_or_muted = True

    return deafened_or_muted


async def process_channel_event(user, channel, event):
    current_time_string = datetime.datetime.now(pytz.timezone('America/Toronto')).isoformat(timespec='seconds')

    # Get the channel to log to based on the server ID if supported
    try:
        log_channel = client.get_channel(guild_to_log_channel_map[channel.guild.id])
    except KeyError:
        print('Unsupported Guild: ' + str(channel.guild) + ' with ID: ' + str(channel.guild.id))
        return

    # Don't mention the user if they can view the server's log channel
    if log_channel.permissions_for(user).read_messages:
        message_string = '[' + current_time_string + '] ' + str(user) + ' ' + event + ' ' + str(channel)
    else:
        message_string = '[' + current_time_string + '] <@' + str(user.id) + '> ' + event + ' ' + str(channel)

    print(str(channel.guild) + ': ' + message_string)
    await log_channel.send(message_string)


@client.event
async def on_voice_state_update(member, before, after):
    if not was_deaf_or_mute_change(before, after):
        if before.channel and after.channel:
            await process_channel_event(user=member, channel=before.channel, event='left')
            await process_channel_event(user=member, channel=after.channel, event='joined')
        elif after.channel:
            await process_channel_event(user=member, channel=after.channel, event='joined')
        else:
            await process_channel_event(user=member, channel=before.channel, event='left')

client.run(bot_secret)
