from discord import app_commands
from discord.ext import commands

from discord import Color, Embed, Interaction, SelectOption
from discord.app_commands import Command, Range
from discord.ext.commands import Bot, Cog, GroupCog
from discord.ui import Select, View

from config import DEBUG_GUILD
from utils.embeds import Error

cog_emojis = {
	"Debug": "\N{MAN}\N{ZERO WIDTH JOINER}\N{PERSONAL COMPUTER}",
	"Fun": "\N{PARTY POPPER}",
	"Miscellaneous": "\N{BLACK QUESTION MARK ORNAMENT}",
	"Moderation": "\N{HAMMER AND WRENCH}",
	"Tags": "\N{LABEL}"
}

def get_command_usage(command: Command):
	parameters = []

	for parameter in command.parameters:
		if parameter.required:
			brackets = "[]"
		else:
			brackets = "()"

		parameters.append(f"`{brackets[0]}{parameter.display_name}{brackets[1]}`")

	return " ".join(parameters)

class Miscellaneous(Cog, description="Other miscellaneous commands"):
	def __init__(self, bot: Bot):
		self.bot = bot

	@app_commands.command(description="Get the bot's latency")
	@app_commands.describe(digits="Number of digits after the decimal point")
	async def ping(self, interaction: Interaction, digits: Range[int, 0, 35]=3):
		latency = self.bot.latency
		latency = round(latency, digits)

		await interaction.response.send_message(embed=Embed(
			title=":ping_pong: Pong!",
			description=f"Latency ≈ `{'%g' % latency}ms`",
			color=Color.blurple()
		))

	@app_commands.command(description="Describe a specific command or view all commands")
	@app_commands.rename(command_name="command")
	@app_commands.describe(command_name="The command to describe")
	async def help(self, interaction: Interaction, command_name: str=None):
		if command_name:
			command = self.bot.tree.get_command(command_name, guild=DEBUG_GUILD)

			if not command:
				await interaction.response.send_message(embed=Error(title=f"Couldn't find command `{command_name}`"))
			else:
				await interaction.response.send_message(embed=Embed(
					title=f"💡 /{command.name} {get_command_usage(command)}",
					description=command.description,
					color=Color.blurple()
				))
		else:
			bot = self.bot

			class CogSelect(Select):
				def __init__(self, *, selected_cog: str=None):
					options = [
						SelectOption(label=cog_name, emoji=cog_emojis[cog_name], description=cog.description)
						for cog_name, cog in bot.cogs.items()
						if cog_name != selected_cog
					]
					
					super().__init__(placeholder="Select a category", options=options)

				async def callback(self, interaction: Interaction):
					cog_name = self.values[0]
					cog = bot.get_cog(cog_name)

					embed = Embed(
						title=f"{cog_emojis[cog.qualified_name]} {cog.qualified_name}",
						description=cog.description,
						color=Color.blurple()
					)

					commands = cog.get_app_commands() or cog.__cog_app_commands_group__.commands

					for command in commands:
						command_name = f"{cog.__cog_group_name__} {command.name}" if isinstance(cog, GroupCog) else command.name
						embed.add_field(
							name=f"/{command_name} {get_command_usage(command)}",
							value=command.description,
							inline=False
						)
					
					await interaction.response.edit_message(
						embed=embed,	
						view=CogSelectView(selected_cog=cog_name)
					)

			class CogSelectView(View):
				def __init__(self, *, selected_cog: str=None):
					super().__init__()

					self.add_item(CogSelect(selected_cog=selected_cog))

			await interaction.response.send_message(
				embed=Embed(
					title="\N{ELECTRIC LIGHT BULB} Help",
					description="Welcome to the help page!\n\nUse \"/help `command`\" for help with a specific\ncommand, or use the dropdown below.",
					color=Color.blurple()
				), view=CogSelectView()
			)

async def setup(bot: commands.Bot):
	await bot.add_cog(Miscellaneous(bot), guild=DEBUG_GUILD)