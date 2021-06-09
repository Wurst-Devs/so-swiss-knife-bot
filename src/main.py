from miniscord import Bot
import logging

import inspirobot

logging.basicConfig(format="[%(asctime)s][%(levelname)s][%(module)s] %(message)s", level=logging.INFO)

bot = Bot(
    "SoSwissKnife",     # name
    "0.1-alpha",    # version
)

bot.register_command(
    "inspi(ration(al)?)?",
    inspirobot.process,
    "inspi: generate an InspiroBot quote",
    "```\n"
    "* inspi\n"
    "\tgenerate an InspiroBot quote\n"
    "```"
)

bot.start()