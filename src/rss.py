import logging
import discord
from miniscord import Bot
import os.path
import os
import json
import requests
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime
import base64

feeds = {}

DATA_DIR = "data"
RSS_FILE = os.path.join(DATA_DIR, "rss.json")
REQUEST_TIMEOUT = 5
SLEEP = 300 # 5 min

if not os.path.exists("data"):
    os.mkdir("data")

if os.path.exists(RSS_FILE):
    try:
        with open(RSS_FILE, "r") as fp:
            feeds = json.load(fp)
            logging.info(f"loaded {len(feeds)} rss feeds")
    except:
        pass


def read_url_xml(url: str) -> ET.Element:
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
        try:
            return ET.fromstring(response.content.decode("utf8"))
        except Exception as e:
            logging.exception(e)
    return None


def parse_feed_timestamp(text):
    return datetime.strptime(text, "%a, %d %b %Y %H:%M:%S %z").timestamp()


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
            for key in feeds:
                channel_id, feed_url, latest_timestamp = feeds[key]
                max_timestamp = latest_timestamp
                links = []
                try:
                    content = read_url_xml(feed_url)
                    channel = content[0]
                    try:
                        feed_timestamp = parse_feed_timestamp(channel.find("lastBuildDate").text)
                    except:
                        feed_timestamp = None
                    for item in channel.findall("item"):
                        link = item.find("link").text
                        strdate = None
                        try:
                            timestamp = parse_feed_timestamp(item.find("pubDate").text)
                            if latest_timestamp is None or timestamp > latest_timestamp:
                                max_timestamp = max(max_timestamp, timestamp)
                                links += [link]
                        except:
                            if feed_timestamp is not None and latest_timestamp is None:
                                latest_timestamp = feed_timestamp
                                max_timestamp = feed_timestamp
                                links += [link]
                    if len(links) > 0:
                        channel = await self.bot.client.fetch_channel(channel_id)
                        if latest_timestamp is not None:
                            for link in links:
                                await channel.send(link)
                        feeds[key] = (channel_id, feed_url, max_timestamp)
                        with open(RSS_FILE, "w") as fp:
                            json.dump(feeds, fp)
                except requests.exceptions.Timeout:
                    pass
                except Exception as e:
                    logging.error(f"FEED: {feed_url}")
                    logging.exception(e)
            await asyncio.sleep(SLEEP)


async def process(client: discord.client, message: discord.Message, *args: str):
    if len(args) < 2:
        await message.channel.send(f"Invalid number of arguments")
        return
    channel_id = message.channel.id
    if len(message.channel_mentions) > 0:
        channel_id = message.channel_mentions[0].id
    url = args[1]
    url_base64 = base64.b64encode(url.encode("utf8")).decode("ascii")
    key = f"{channel_id}/{url_base64}"
    if "cancel" in args or "unsubscribe" in args:
        if key in feeds:
            del feeds[key]
            await message.channel.send(f"RSS Feed unsubscribed")
        else:
            await message.channel.send(f"Cannot find specified RSS feed")
    elif key in feeds:
        await message.channel.send(f"RSS Feed already subscribed for this channel")
    else:
        content = read_url_xml(url)
        if content is not None:
            try:
                title = content[0].find("title").text
                feeds[key] = (channel_id, url, None)
                await message.channel.send(f"RSS Feed subscribed: __{title}__")
            except Exception as e:
                logging.exception(e)
                await message.channel.send(
                    f"Cannot subscribe to RSS Feed: invalid format"
                )
                return
        else:
            await message.channel.send(
                f"Cannot subscribe to RSS Feed: cannot read feed from URL"
            )
            return
    with open(RSS_FILE, "w") as fp:
        json.dump(feeds, fp)
