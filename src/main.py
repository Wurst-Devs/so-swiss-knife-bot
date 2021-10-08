from miniscord import Bot
import logging

import inspirobot
import cat
import schedule

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s][%(module)s] %(message)s", level=logging.INFO
)

bot = Bot(
    "SoSwissKnife",  # name
    "0.2-alpha",  # version
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
    schedule.process,
    "schedule: schedule command",
    "```\n"
    '* schedule "message content" "crontab format" (optionnal channel)\n'
    '* schedule "message content" cancel\n'
    "```",
)


async def on_connect() -> bool:
    schedule.Worker(bot).start()
    return True


bot.register_event(on_connect)

bot.start()
