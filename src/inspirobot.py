import discord
import requests

async def process(client: discord.client, message: discord.Message, *args: str):
    try:
        async with message.channel.typing():
            r = requests.get('https://inspirobot.me/api?generate=true')
            await message.channel.send(r.text)
    except Exception as e:
        await message.channel.send(f"Python Exception:\n```{e}```")