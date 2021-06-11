import discord
import requests
import io
import time

async def process(client: discord.client, message: discord.Message, *args: str):
    try:
        if "tags" in args:
            await cat_tags(message)
        else:
            await random_cat(message, *args)
    except Exception as e:
        await message.channel.send(f"Python Exception:\n```{e}```")

async def cat_tags(message: discord.Message):
    uri = "https://cataas.com/api/tags"
    r = requests.get(uri)
    if r.status_code == 200:
        await message.channel.send(f"All cats tags:")
        tags = r.json()
        output = ""
        while len(tags) > 0:
            output += tags.pop(0)
            if len(tags) > 0 and len(output + tags[0]) + 8 > 2000:
                await message.channel.send(f"```{output}```")
                output = ""
            elif len(tags) > 0:
                output += ", "
        await message.channel.send(f"```{output}```")
    else:
        await message.channel.send(f"Could not get a cat tags D: (`{r.status_code})")

def get_filename(r: requests.Response):
    ctype = r.headers["Content-Type"]
    if ctype.startswith("image/"):
        return f"{int(time.time())}.{ctype[6:]}"
    else:
        return f"{int(time.time())}"

async def random_cat(message: discord.Message, *args: str):
    uri = "https://cataas.com/cat"
    if len(args) >= 2:
        uri += f"/{args[1]}"
    r = requests.get(uri)
    if r.status_code == 200:
        with io.BytesIO(r.content) as f:
            await message.channel.send("", file=discord.File(f, filename=get_filename(r)))
    else:
        await message.channel.send(f"Could not get a cat D: ({r.status_code}), see tags by adding `tags`")