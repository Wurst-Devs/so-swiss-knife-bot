import logging
import discord
from miniscord import Bot
from croniter import croniter
from datetime import datetime
import dateutil.tz
import asyncio
import os.path
import os
import json

scheduled = {}

tz = dateutil.tz.gettz("Europe/Paris")

DATA_DIR = "data"
SCHEDULED_FILE = os.path.join(DATA_DIR, "scheduled.json")

if not os.path.exists("data"):
    os.mkdir("data")

if os.path.exists(SCHEDULED_FILE):
    try:
        with open(SCHEDULED_FILE, "r") as fp:
            scheduled = json.load(fp)
            logging.info(f"loaded {len(scheduled)} events")
    except:
        pass


class Worker:
    def __init__(
        self,
        bot: Bot,
    ):
        self.bot = bot
        self.loop = asyncio.get_event_loop()

    def start(self):
        asyncio.run_coroutine_threadsafe(self.process(), self.loop)

    async def process(self):
        while True:
            local_date = datetime.now(tz)
            for (
                channel_id,
                message_content,
                crontab,
                original_channel_id,
                original_message_id,
            ) in scheduled.values():
                try:
                    if croniter.match(crontab, local_date):
                        logging.info(f"executing: {message_content}")
                        channel = await self.bot.client.fetch_channel(channel_id)
                        if message_content.startswith("self "):
                            message_content = message_content.lstrip("self ")
                            original_channel = await self.bot.client.fetch_channel(
                                original_channel_id
                            )
                            original_message = await original_channel.fetch_message(
                                original_message_id
                            )
                            original_message.channel = channel
                            original_message.content = (
                                f"{self.bot.client.user.mention} {message_content}"
                            )
                            original_message.mentions += [self.bot.client]
                            await channel.send(original_message.content)
                            await self.bot.on_message(original_message)
                        else:
                            await channel.send(message_content)
                except Exception as e:
                    logging.exception(e)
            await asyncio.sleep(60)


async def process(client: discord.client, message: discord.Message, *args: str):
    if len(args) < 3:
        await message.channel.send(f"Invalid number of arguments")
        return
    if args[2] != "cancel" and not croniter.is_valid(args[2]):
        await message.channel.send(f"Invalid crontab")
        return
    channel_id = message.channel.id
    if len(message.channel_mentions) > 0:
        channel_id = message.channel_mentions[0].id
    key = f"{channel_id}/{args[1]}"
    if args[2] == "cancel":
        if key in scheduled:
            del scheduled[key]
            await message.channel.send(f"Message canceled")
        else:
            await message.channel.send(f"Cannot find message")
    else:
        scheduled[key] = (channel_id, args[1], args[2], message.channel.id, message.id)
        local_date = datetime.now(tz)
        next = croniter(args[2], local_date).get_next(datetime)
        await message.channel.send(f"Message scheduled (next: {next:%Y-%m-%d %H:%M})")
    with open(SCHEDULED_FILE, "w") as fp:
        json.dump(scheduled, fp)
