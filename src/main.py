from miniscord import Bot
import discord
import logging
import sys
import random
import os

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s][%(module)s] %(message)s", level=logging.INFO
)

import inspirobot
import cat
import schedule
import lock
import rss
import caps_alert
import distopia


async def on_connect() -> bool:
    if lock.is_locked():
        logging.info(f"already running bot")
        sys.exit(0)
    lock.lock()
    schedule.Worker(bot).start()
    rss.Worker(bot).start()
    return True


async def on_message(client: discord.client, message: discord.Message):
    await caps_alert.on_message(message)
    await distopia.on_message(message)


with open(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "quotes.txt"))
) as file:
    quotes = [line.strip() for line in file]


async def on_mention(client: discord.client, message: discord.Message, *args: str):
    await message.channel.send(
        random.choice(quotes).replace("%author", message.author.mention)
    )


bot = Bot(
    "SoSwissKnife",  # name
    "0.5.3",  # version
)

bot.log_calls = True

bot.register_command(
    "inspi(ration(al)?)?",
    inspirobot.process,
    "inspi: generate an InspiroBot quote",
    "```\n"
    "* inspi\n"
    "\tgenerate an InspiroBot quote (<https://inspirobot.me/>)\n"
    "```",
)

bot.register_command(
    "cat",
    cat.process,
    "cat: get a cat",
    "```\n" "* cat (gif|cute|...)\n" "\tget a cat\n" "```",
)

bot.register_command(
    "schedule",
    schedule.process_schedule,
    "schedule: schedule command",
    "```\n"
    '* schedule "message content" "crontab format" (optionnal channel)\n'
    '* schedule "message content" cancel\n'
    "```",
)

bot.register_command(
    "scheduled",
    schedule.process_scheduled,
    "scheduled: list scheduled command",
    "```\n" "* scheduled (optionnal channel)\n" "```",
)

bot.register_command(
    "rss",
    rss.process,
    "rss: subscribe to RSS feed",
    "```\n" "* rss URL (optionnal channel) (optional title regex)\n" "* rss URL cancel\n" "```",
)

bot.register_command(
    "caps",
    caps_alert.process,
    "caps: react to caps locked messages",
    "```\n" "* caps (discord emote)\n" "* caps off\n" "```",
)

bot.register_command(
    "distopia",
    distopia.process,
    "distopia: react to words starting with di or cri",
    "```\n" "* distopia (floating chance <=1)\n" "* distopia off\n" "```",
)


bot.register_event(on_connect)

bot.register_watcher(on_message)

bot.register_fallback(on_mention)

bot.start()
