import os
import traceback
from dotenv import load_dotenv
import discord
from discord.ext import commands

startup_extensions = ["verification",
                      "security",
                      "admins",
                      "fun",
                      "tortoise_server",
                      "other",
                      "reddit",
                      "help",
                      "music",
                      "cmd_error_handler"]


class Bot(commands.Bot):
    DEFAULT_PREFIX = "!"

    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, command_prefix=Bot.DEFAULT_PREFIX, **kwargs)


bot = Bot()


@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension_path):
    """
    Loads an extension.
    :param extension_path: full path, dotted access, example:
                           cogs.admin

    """
    bot.load_extension(extension_path)
    await ctx.send(f"{extension_path} loaded.")


@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension_path):
    """
    Unloads an extension.
    :param extension_path: full path, dotted access, example:
                           cogs.admin

    """
    bot.unload_extension(extension_path)
    await ctx.send(f"{extension_path} unloaded.")


@bot.event
async def on_ready():
    print("Successfully logged in and booted...!")
    print(f"Logged in as {bot.user.name} with ID {bot.user.id} \t d.py version: {discord.__version__}")

if __name__ == "__main__":
    load_dotenv()

    for extension in startup_extensions:
        cog_path = f"cogs.{extension}"
        try:
            bot.load_extension(cog_path)
            print(f"Loaded {cog_path}")
        except Exception as e:
            traceback_msg = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
            print(f"Failed to load cog {cog_path} - traceback:{traceback_msg}")

    bot.run(os.getenv("BOT_TOKEN"))
