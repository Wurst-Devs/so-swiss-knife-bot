from miniscord import Bot
import discord


async def hello(client: discord.client, message: discord.Message, *args: str):
    await message.channel.send("Hello!")

bot = Bot(
    "SoSwissKnife",     # name
    "0.1-alpha",    # version
)
bot.register_command(
    "hello",                    # command text (regex)
    hello,                      # command function
    "hello: says 'Hello!'",     # short help
    "```\n"                    # long help
    "* |help\n"
    "\tSays 'Hello!'.\n"
    "```"
)
bot.start()  # this bot respond to "|help", "|info" and "|hello"