import os
import sqlite3
import discord
from discord import app_commands
from discord.ext import commands

from discord import Intents, Interaction
from discord.app_commands import CommandTree
from discord.ext.commands import Bot

from discord.errors import InteractionResponded
from discord.app_commands.errors import CheckFailure

from config import DEBUG_GUILD, TOKEN
from utils.embeds import Error
from utils.sqlite import Cursor

connection = sqlite3.connect("tags.db")
cursor = Cursor(connection)

cursor.execute("CREATE TABLE IF NOT EXISTS tags (name TEXT PRIMARY KEY, content TEXT, uses INTEGER, author INTEGER, timestamp INTEGER)")

class Bot(Bot):
	def __init__(self):
		self.cursor = cursor

		intents = Intents.all()

		super().__init__(
			command_prefix="terry,",
			strip_after_prefix=True,
			help_command=None,
			tree_cls=CommandTree,
			intents=intents
		)

	async def setup_hook(self):
		for extension in os.listdir("cogs"):
			if extension.endswith(".py"):
				await self.load_extension(f"cogs.{extension[:-3]}")

		self.tree.copy_global_to(guild=DEBUG_GUILD)

	async def close(self):
		self.cursor.commit()
		self.cursor.close()

		await super().close()

bot = Bot()
	
bot.run(TOKEN)