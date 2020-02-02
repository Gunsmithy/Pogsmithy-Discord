import discord
import datetime
import pytz

sasstest_guild_id = 354836976492347394
sasstest_channel_id = 354836976949788674
sass_guild_id = 100781489800609792
sass_log_channel_id = 673315310752890929

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
    message_string = '[' + current_time_string + '] ' + str(user) + ' ' + event + ' ' + str(channel)
    if channel.guild.id == sasstest_guild_id:
        print(str(channel.guild) + ': ' + message_string)
        await client.get_channel(sasstest_channel_id).send(message_string)
    elif channel.guild.id == sass_guild_id:
        print(str(channel.guild) + ': ' + message_string)
        await client.get_channel(sass_log_channel_id).send(message_string)
    else:
        print('Unsupported Guild: ' + str(channel.guild) + ' with ID: ' + str(channel.guild.id))


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
