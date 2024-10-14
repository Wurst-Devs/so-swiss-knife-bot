import discord
from typing import *
from lib.data import load_data, save_data
import re
import random


config = load_data("distopia", default={})


async def process(client: discord.client, message: discord.Message, *args: str):
    guild_id = message.guild.id if message.guild is not None else message.channel.id
    if len(args) != 2:
        await message.reply("Invalid number of arguments")
    elif args[1].lower() == "off":
        config[str(guild_id)] = None
        await message.add_reaction("✅")
    else:
        try:
            config[str(guild_id)] = float(args[1])
        except:
            await message.add_reaction("❎")
            return
        await message.add_reaction("✅")
    save_data("distopia", config)


async def on_message(message: discord.Message):
    guild_id = message.guild.id if message.guild is not None else message.channel.id
    if (
        str(guild_id) in config
        and config[str(guild_id)] is not None
        and len(message.content) > 0
    ):
        matches = re.findall(r"(di|cri)(\w+)", message.content, re.IGNORECASE)
        for a, b in matches:
            if random.random() < config[str(guild_id)]:
                if a.lower() == "di":
                    await message.channel.send(b.capitalize())
                else:
                    await message.channel.send(b.upper())
