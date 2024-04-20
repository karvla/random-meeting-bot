#!/usr/bin/python3
import random
import datetime
from zoneinfo import ZoneInfo
import os
from discord.ext import commands
from discord import Intents, EntityType, PrivacyLevel
from dotenv import load_dotenv
import asyncio

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if BOT_TOKEN is None:
    exit("No BOT_TOKEN set")

SERVER_ID = os.environ.get("SERVER_ID")
if SERVER_ID is None:
    exit("No SERVER_ID set")
SERVER_ID = int(SERVER_ID)

earliest_hour = int(os.environ.get("EARLIEST_HOUR", 18))
latest_hour = int(os.environ.get("LATEST_HOUR", 21))
period_days = int(os.environ.get("PERIOD_DAYS", 7))
time_zone = os.environ.get("TZ", "Europe/Stockholm")

bot = commands.Bot(intents=Intents.default(), command_prefix="!")


async def schedule_meeting():
    current_date = datetime.datetime.now().date()
    date_range = [current_date + datetime.timedelta(days=i) for i in range(1, period_days)]
    meeting_day = random.choice(date_range)

    meeting_time = datetime.datetime(
        meeting_day.year,
        meeting_day.month,
        meeting_day.day,
        random.randint(earliest_hour, latest_hour - 1),
        random.choice([0, 15, 30, 45]),
        tzinfo=ZoneInfo(time_zone)
    )

    server = bot.get_guild(SERVER_ID)
    if server is None:
        exit(f"Wrong server id '{SERVER_ID}' or no permissions")
    text_channel = server.text_channels[0]
    voice_channel = server.voice_channels[0]

    meeting = await server.create_scheduled_event(
        name="Random meeting",
        start_time=meeting_time,
        entity_type=EntityType.voice,
        channel=voice_channel,
        privacy_level=PrivacyLevel.guild_only,
    )
    if meeting is None:
        exit("Could not create meeting")
    await text_channel.send(f"new random meeting! {meeting.url}")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    await schedule_meeting()
    await bot.close()


bot.run(BOT_TOKEN)
