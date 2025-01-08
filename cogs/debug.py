from async_eval import eval as async_eval
from contextlib import redirect_stdout
from time import perf_counter

from discord import app_commands
from discord.ext import commands
from discord.utils import find

from discord import Color, Embed, Interaction, Object, TextStyle
from discord.ui import Modal, TextInput

from discord.errors import InteractionResponded, Forbidden
from discord.app_commands.errors import CommandSyncFailure
from discord.ext.commands.errors import ExtensionNotFound, ExtensionNotLoaded

from config import DEBUG_GUILD
from utils.embeds import Error

class Debug(commands.Cog, description="Commands for debugging the bot", group_extras={"h": True}):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.cursor = self.bot.cursor

	async def interaction_check(self, interaction: Interaction):
		return interaction.user.id == 276384743266975746
	
	@app_commands.command(name="eval", description="Reload one or all extenions")
	@app_commands.describe(code="Code to evaluate")
	async def evaluate(self, interaction: Interaction, code: str=None):
		bot = self.bot
		cursor = self.cursor

		async def evaluate_code(interaction: Interaction, code: str):
			env = {
				"_bot": bot,
				"_cursor": cursor,
				"_interaction": interaction,
				"_channel": interaction.channel,
				"_guild": interaction.guild,
				"_send_message": interaction.response.send_message,
				"_send_modal": interaction.response.send_modal
			}

			try:
				start_time = perf_counter()
			
				with redirect_stdout(None):
					result = async_eval(code, env)

				end_time = perf_counter()
			except Exception as exc:
				embed=Error(
					title=f"Code execution failed (`{exc.__class__.__name__}`)",
					description=f"```\n{exc.__class__.__name__}: {exc}\n```"
				)
			else:
				elapsed_time = end_time - start_time
				suffix = "ms"

				if elapsed_time < 0.01:
					elapsed_time *= 1000
					suffix = "\N{GREEK SMALL LETTER MU}s"

				elapsed_time = round(elapsed_time, 2)

				embed = Embed(
					title=f"</> Code executed in `{elapsed_time}{suffix}`",
					description=f"```\n{result}\n```" if result else None,
					color=Color.blurple()
				)
			
			try:
				await interaction.response.send_message(embed=embed)
			except InteractionResponded:
				if interaction.message:
					await interaction.message.reply(embed=embed)
				else:
					await interaction.followup.send(embed=embed)

		if code == None:
			class CodeModal(Modal, title="Create Tag"):
				code_input = TextInput(label="Code", style=TextStyle.paragraph)

				async def on_submit(self, interaction: Interaction):
					await evaluate_code(interaction, self.code_input.value)

			await interaction.response.send_modal(CodeModal())
		else:
			await evaluate_code(interaction, code)

	@app_commands.command(description="Reload one or all extenions")
	@app_commands.rename(extension_name="extension")
	@app_commands.describe(extension_name="Extension to reload")
	async def reload(self, interaction: Interaction, extension_name: str=None):
		if extension_name:
			extension_name = extension_name.lower()

			extension = find(
				lambda ext: ext.split(".")[- 1].startswith(extension_name),
				self.bot.extensions
			)

			try:
				await self.bot.reload_extension(extension)
			
				await interaction.response.send_message(
					embed=Embed(
						title=f":arrows_clockwise: Reloaded extension `{extension}`",
						color=0x3b88c3
					)
				)
			except ExtensionNotLoaded:
				try:
					await self.bot.load_extension(extension)
			
					await interaction.response.send_message(
						embed=Embed(
							title=f":arrow_heading_down: Loaded extension `{extension}`",
							color=0x3b88c3
						),
						ephemeral=True
					)
				except ExtensionNotFound:
					return await interaction.response.send_message(
						embed=Error(f"Extension not found"),
						ephemeral=True
					)
		else:
			for ext in self.bot.extensions.copy():
				await self.bot.reload_extension(ext)

			await interaction.response.send_message(
				embed=Embed(
					title=f":arrows_clockwise: Reloaded all extensions",
					color=0x3b88c3
				)
			)

	@app_commands.command(description="Sync the command tree with Discord")
	async def sync(self, interaction: Interaction, guild_id: int=None):
		if guild_id:
			try:
				await self.bot.tree.sync(guild=Object(guild_id))
				
				await interaction.response.send_message(
					embed=Embed(
						title=f":satellite: Synced commands to guild with ID `{guild_id}`",
						color=0x99aab5
					)
				)
			except Forbidden:
				await interaction.response.send_message(
					embed=Error(f"Bot not present in guild with ID `{guild_id}`"),
					ephemeral=True
				)
			except CommandSyncFailure:
				await interaction.response.send_message(
					embed=Error(f"Guild with ID `{guild_id}` not found"),
					ephemeral=True
				)
		else:
			await interaction.response.defer(ephemeral=True, thinking=True)

			await self.bot.tree.sync(guild=DEBUG_GUILD)

			await interaction.followup.send(
				embed=Embed(
					title=f":satellite: Globally synced commands to all guilds",
					color=0x99aab5
				)
			)
		
async def setup(bot: commands.Bot):
	await bot.add_cog(Debug(bot), guild=DEBUG_GUILD)