import argparse
import datetime
import discord
import os
import pytz
import sys

guild_to_log_channel_map = {
    354836976492347394: 354836976949788674,  # SassTest
    100781489800609792: 673315310752890929,  # Sassy Squad
}

client = discord.Client()

banned_words_original = {'joel', 'ellie', 'tlou', 'naughtydog', 'lastofus'}
banned_words_permutated = set().union(banned_words_original)
leet_speak_map = {
    'a': ['@'],
    'o': ['0'],
    'i': ['1', 'l', '!'],
    'l': ['1', 'i', '!'],
    't': ['7'],
    's': ['5'],
    'e': ['3'],
    'b': ['8']
}


def create_permutations(passed_word):
    index = 0
    while index < len(passed_word):
        original_word_start = passed_word[:index]
        original_word_end = passed_word[index:]
        for letter in original_word_end:
            if letter in leet_speak_map.keys():
                for new_letter in leet_speak_map[letter]:
                    new_word = original_word_start + original_word_end.replace(letter, new_letter)
                    if new_word not in banned_words_permutated:
                        banned_words_permutated.add(new_word)
                        create_permutations(new_word)
        index += 1


for original_word in banned_words_original:
    create_permutations(original_word)


def spoiler_check(message_passed):
    formatted = message_passed.replace(' ', '')
    formatted = formatted.lower()
    length = len(formatted)
    substring_list = [formatted[i:j + 1] for i in range(length) for j in range(i, length)]
    for substring in substring_list:
        if substring in banned_words_permutated:
            return True
    return False


def read_secret_file(file_path):
    with open(file_path, 'r') as auth_file:
        return auth_file.readline()


def config():
    bot_secret = os.getenv('POGSMITHY_DISCORD_SECRET')
    bot_secret_file = os.getenv('POGSMITHY_DISCORD_SECRET_FILE')
    parser = argparse.ArgumentParser(description='Run Pogsmithy for Discord.')
    parser.add_argument('--secret', dest='secret', help='The Discord secret used to run the bot.')
    parser.add_argument('--secret-file', dest='secret_file', help='The path to the file containing the Discord secret '
                                                                  'used to run the bot.')
    args = parser.parse_args()

    if args.secret is not None:
        print('Using --secret command-line argument...')
        return args.secret
    if args.secret_file is not None:
        print('Using --secret-file command-line argument...')
        return read_secret_file(args.secret_file)
    if bot_secret is not None:
        print('Using POGSMITHY_DISCORD_SECRET environment variable...')
        return bot_secret
    if bot_secret_file is not None:
        print('Using POGSMITHY_DISCORD_SECRET_FILE environment variable...')
        return read_secret_file(bot_secret_file)

    print('Bot secret could not be derived from environment or arguments. Aborting...')
    sys.exit(1)


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


@client.event
async def on_message(message):
    if message.author != client.user and spoiler_check(message.content):
        await message.delete()
        channel = message.channel
        await channel.send(f'<@{str(message.author.id)}> No Last of Us 2 spoilers! :angry:')


def main():
    bot_secret = config()
    client.run(bot_secret)


if __name__ == "__main__":
    main()
