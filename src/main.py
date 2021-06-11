from miniscord import Bot
import logging

import inspirobot
import cat

logging.basicConfig(format="[%(asctime)s][%(levelname)s][%(module)s] %(message)s", level=logging.INFO)

bot = Bot(
    "SoSwissKnife",     # name
    "0.2-alpha",    # version
)

bot.log_calls = True

bot.register_command(
    "inspi(ration(al)?)?",
    inspirobot.process,
    "inspi: generate an InspiroBot quote",
    "```\n"
    "* inspi\n"
    "\tgenerate an InspiroBot quote (<https://inspirobot.me/>)\n"
    "```"
)

bot.register_command(
    "cat",
    cat.process,
    "cat: get a cat",
    "```\n"
    "* cat (gif|cute|...)\n"
    "\tget a cat\n"
    "```"
)

bot.start()
