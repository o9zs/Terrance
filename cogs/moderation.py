from discord import app_commands
from discord import Interaction, Member, Message, User
from discord.ext import commands

from config import DEBUG_GUILD 
from utils.embeds import Success, Warning

class Moderation(commands.Cog, description="Commands for moderating servers and members"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(description="Bulk delete messages")
	@app_commands.describe(amount="Number of messages to delete", user="The user who's messages to delete")
	async def purge(
		self,
		interaction: Interaction,
		amount: app_commands.Range[int, 1, 100],
		user: User | Member=None,
		reason: str=None
	):
		def check_author(message: Message):
			return user == None or message.author == user
		
		purged = await interaction.channel.purge(limit=amount, check=check_author, reason=reason)

		amount = len(purged)

		if amount == 0:
			return await interaction.response.send_message(embed=Warning(title="No messages found"))

		await interaction.response.send_message(embed=Success(title=f"Successfully purged {amount} message{'s'[:amount ^ 1]}"))

async def setup(bot: commands.Bot):
	await bot.add_cog(Moderation(bot), guild=DEBUG_GUILD)
