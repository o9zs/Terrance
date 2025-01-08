import random

from discord import app_commands
from discord import Interaction, Embed
from discord.app_commands import Choice
from discord.ext import commands

from config import DEBUG_GUILD

class Fun(commands.Cog, description="Super duper fun commands!"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(description="Roll a game die")
	async def dice(self, interaction: Interaction, sides: int=6):
		number = random.randint(1, sides)

		await interaction.response.send_message(embed=Embed(
			title=f":game_die: You rolled a... `{number}`!",
			color=0xdd2e44
		))

	@app_commands.command(description="Flip a coin")
	async def coin(self, interaction: Interaction):
		side = random.choice(["heads", "tails"])

		await interaction.response.send_message(embed=Embed(
			title=f":coin: It landed on... `{side}`!",
			color=0xffac33
		))
		
	@app_commands.command(name="8ball", description="Ask a yes/no question to the magic 8-ball...")
	@app_commands.choices(
		answer=[
			Choice(name="positive", value="positive"),
			Choice(name="negative", value="negative"),
			Choice(name="confused", value="confused")
		]
	)
	async def eight_ball(self, interaction: Interaction, question: str, answer: Choice[str]=None):
		responses = {
			"positive": [
				"Yes.",
				"It is certain.",
				"Without a doubt",
				"Yep, definitely.",
				"Most likely, yeah.",
				"Outlook's lookin' good!"
			],
			"negative" : [
				"No.",
				"Nope.",
				"Nuh-uh.",
				"Extremely doubtful.",
				"No. Definitely not.",
				"Outlook isn't looking good..."
			],
			"confused": [
				"Huh?",
				"What?",
				"I don't know, man",
				"Signs point to... uhh... err...",
				"I... don't know how to answer that."
			]
		}

		if answer:
			response = random.choice(responses[answer.value])
		else:
			response = random.choice([response for responses in responses.values() for response in responses])

		await interaction.response.send_message(embed=Embed(
			title=f":8ball: {response}",
			color=0x31373d
		))

async def setup(bot: commands.Bot):
	await bot.add_cog(Fun(bot), guild=DEBUG_GUILD)
