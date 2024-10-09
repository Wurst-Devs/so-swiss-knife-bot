import logging
import discord
from miniscord import Bot
import requests
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime
import base64
from lib.data import load_data, save_data
import re
from dateutil import parser

REQUEST_TIMEOUT = 5
SLEEP = 300  # 5 min

feeds = load_data("rss", default={})

# convert from v1 to v2
for key in feeds:
    if len(feeds[key]) < 5:
        feeds[key] = tuple(list(feeds[key]) + [None, []])


def read_url_xml(url: str) -> ET.Element:
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.content.decode("utf8"))
            for elem in root.iter():
                elem.tag = elem.tag.split('}')[-1]
            return root
        except Exception as e:
            logging.exception(e)
    return None


def find_first(node: ET.Element, *names: str) -> ET.Element:
    for name in names:
        if node.find(name) is not None:
            return node.find(name)
    return None


def parse_feed_timestamp(text: str) -> float:
    return parser.parse(text).timestamp()


def get_feed_channel(content: ET.Element) -> ET.Element:
    if content is None:
        return None
    if content.tag == 'rss':
        return content.find('channel')
    elif content.tag == 'feed':
        return content
    else:
        return None


class Worker:
    def __init__(
        self,
        bot: Bot,
    ):
        self.bot = bot
        self.loop = asyncio.get_event_loop()

    def start(self):
        logging.info("Running worker...")
        asyncio.run_coroutine_threadsafe(self.process(), self.loop)

    async def process(self):
        while True:
            for key in feeds:
                try:
                    channel_id, feed_url, _, regex, seen = feeds[key]
                    try:
                        content = read_url_xml(feed_url)
                        channel = get_feed_channel(content)
                        if channel is not None:
                            title = channel.find("title").text
                            logging.info(f"Reading: \"{title}\" (regex: {regex})")
                            items = channel.findall("item") + channel.findall("entry")
                            new_seen = []
                            links = []
                            for item in items:
                                link_node = item.find("link")
                                link = link_node.text if link_node.text is not None else link_node.attrib['href']
                                new_seen += [link]
                                title = item.find("title")
                                discarding = False
                                if regex is not None:
                                    if title is None or re.search(regex, title.text, re.IGNORECASE) is None:
                                        discarding = True
                                        new_seen.remove(link)
                                if not discarding and link not in seen:
                                    logging.info(f"* {link}")
                                    links += [link]
                            if len(links) > 0:
                                channel = await self.bot.client.fetch_channel(channel_id)
                                if len(new_seen) != len(links):
                                    for link in links:
                                        await channel.send(link)
                                feeds[key] = (channel_id, feed_url, None, regex, new_seen)
                                save_data("rss", feeds)
                    except requests.exceptions.Timeout:
                        pass
                    except Exception as e:
                        logging.error(f"FEED: {feed_url}")
                        logging.exception(e)
                except Exception as e:
                    logging.exception(e)
            await asyncio.sleep(SLEEP)


async def process(client: discord.client, message: discord.Message, *args: str):
    if len(args) < 2:
        await message.channel.send(f"Invalid number of arguments")
        return
    if len(message.channel_mentions) > 1:
        await message.channel.send(f"Too many channels")
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
        regex = None
        if len(args) > 2 + len(message.channel_mentions):
            regex = args[-1]
            try:
                re.compile(regex)
            except:
                await message.channel.send(f"Invalid regex")
                return
        content = read_url_xml(url)
        if content is not None:
            channel = get_feed_channel(content)
            if channel is None:
                await message.channel.send(
                    f"Cannot subscribe to RSS Feed: invalid format"
                )
                return
            try:
                title = channel.find("title").text
                feeds[key] = (channel_id, url, None, regex, [])
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
    save_data("rss", feeds)
