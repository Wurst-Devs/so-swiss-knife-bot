import discord
from typing import *
from lib.data import load_data, save_data


config = load_data("caps_alert", default={})


async def process(client: discord.client, message: discord.Message, *args: str):
    guild_id = message.guild.id if message.guild is not None else message.channel.id
    if len(args) != 2:
        await message.reply("Invalid number of arguments")
    elif args[1].lower() == "off":
        config[str(guild_id)] = None
        await message.add_reaction("✅")
    else:
        try:
            await message.add_reaction(args[1])
        except:
            await message.add_reaction("❎")
            return
        await message.add_reaction("✅")
        config[str(guild_id)] = args[1]
    save_data("caps_alert", config)


async def on_message(message: discord.Message):
    guild_id = message.guild.id if message.guild is not None else message.channel.id
    try:
        if (
            str(guild_id) in config
            and config[str(guild_id)] is not None
            and message.content != None
            and len(message.content) > 0
            and message.content == message.content.upper()
            and message.content != message.content.lower()
        ):
            await message.add_reaction(config[str(guild_id)])
    except:
        pass
