from miniscord import Bot
import logging
import sys

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s][%(module)s] %(message)s", level=logging.INFO
)

import inspirobot
import cat
import schedule
import lock
import rss

bot = Bot(
    "SoSwissKnife",  # name
    "0.3.1",  # version
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
    "```\n"
    '* scheduled (optionnal channel)\n'
    "```",
)

bot.register_command(
    "rss",
    rss.process,
    "rss: subscribe to RSS feed",
    "```\n" "* rss URL (optionnal channel)\n" "* rss URL cancel\n" "```",
)


async def on_connect() -> bool:
    if lock.is_locked():
        logging.info(f"already running bot")
        sys.exit(0)
    lock.lock()
    schedule.Worker(bot).start()
    rss.Worker(bot).start()
    return True


bot.register_event(on_connect)

bot.start()
