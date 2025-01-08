from datetime import datetime

from discord import app_commands
from discord.ext import commands

from discord import Color, Embed, Interaction, TextStyle, User
from discord.ext.commands import Bot, GroupCog
from discord.ui import Modal, TextInput

from config import DEBUG_GUILD
from utils.embeds import Error, Success
from utils.sqlite import Cursor

class Tags(GroupCog, group_name="tag", description="User-generated tag system"):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.cursor: Cursor = self.bot.cursor

	async def tag_autocomplete(self, interaction: Interaction, current_value: str):
		matching_tags = self.cursor.get_records(
			"SELECT name FROM tags WHERE name LIKE ?%",
			current_value
		)

		print(matching_tags)

		return [
			app_commands.Choice(name=tag.name, value=tag.name)
			for tag in matching_tags
		]

	async def owned_tag_autocomplete(self, interaction: Interaction, current_value: str):
		matching_tags = self.cursor.get_records(
			"SELECT name FROM tags WHERE name LIKE ?% AND author = ?",
			current_value, interaction.user.id
		)

		print(matching_tags)

		return [
			app_commands.Choice(name=tag.name, value=tag.name)
			for tag in matching_tags
		]

	@app_commands.command(description="Create a new tag")
	@app_commands.describe(
		name="Your tag's name",
		content="The text content of your tag"
	)
	async def create(self, interaction: Interaction, name: str, content: str=None):
		cursor = self.cursor

		if cursor.get_field("SELECT name FROM tags WHERE name = ?", name):
			return await interaction.response.send_message(embed=Error(
				title="That tag already exists"
			))

		author_id = interaction.user.id
		timestamp = datetime.timestamp(datetime.now())

		async def create_tag(interaction: Interaction, name: str, content: str):
			cursor.execute(
				"INSERT INTO tags VALUES (?, ?, ?, ?, ?)",
				name, content, 0, author_id, timestamp
			)

			await interaction.response.send_message(embed=Success(
				title=f"Tag `{name}` created"
			))
	
		if content == None:
			class CreateModal(Modal, title="Create Tag"):
				name_input = TextInput(label="Name", default=name)
				content_input = TextInput(label="Content", style=TextStyle.paragraph)

				async def on_submit(self, interaction: Interaction):
					name = self.name_input.value
					content = self.content_input.value

					await create_tag(interaction, name, content)

			await interaction.response.send_modal(CreateModal())
		else:
			await create_tag(interaction, name, content)

	@app_commands.command(description="Edit an existing tag")
	@app_commands.describe(
		name="Your tag's name",
		content="The new content of your tag"
	)
	@app_commands.autocomplete(name=owned_tag_autocomplete)
	async def edit(self, interaction: Interaction, name: str, content: str=None):
		cursor = self.cursor

		tag = cursor.get_record("SELECT author FROM tags WHERE name = ?", name)

		if tag == None:
			return await interaction.response.send_message(embed=Error(
				title="That tag doesn't exist"
			))
		elif tag.author != interaction.user.id:
			return await interaction.response.send_message(embed=Error(
				title="That isn't your tag"
			))
		
		async def edit_tag(interaction: Interaction, content: str):
			cursor.execute("UPDATE tags SET content = ? WHERE name = ?", content, name)

			await interaction.response.send_message(embed=Success(
				title=f"Tag `{name}` edited"
			))

		if content == None:
			class EditModal(Modal, title="Edit Tag"):
				content_input = TextInput(label="Content", style=TextStyle.paragraph)

				async def on_submit(self, interaction: Interaction):
					content = self.content_input.value
					
					await edit_tag(interaction, content)

			await interaction.response.send_modal(EditModal())
		else:
			await edit_tag(interaction, content)


	@app_commands.command(description="Get an existing tag's content")
	@app_commands.describe(name="The tag's name")
	@app_commands.autocomplete(name=tag_autocomplete)
	async def get(self, interaction: Interaction, name: str):
		tag = self.cursor.get_record("SELECT * FROM tags WHERE name = ?", name)

		if tag == None:
			return await interaction.response.send_message(embed=Error(
				title="That tag doesn't exist"
			))
		
		self.cursor.execute("UPDATE tags SET uses = uses + 1 WHERE name = ?", name)

		await interaction.response.send_message(tag.content)

	@app_commands.command(description="Delete an existing tag")
	@app_commands.describe(name="Your tag's name")
	@app_commands.autocomplete(name=owned_tag_autocomplete)
	async def delete(self, interaction: Interaction, name: str):
		tag = self.cursor.get_record("SELECT author FROM tags WHERE name = ?", name)

		if tag == None:
			return await interaction.response.send_message(embed=Error(
				title="That tag doesn't exist"
			))
		elif tag.author != interaction.user.id:
			return await interaction.response.send_message(embed=Error(
				title="That isn't your tag"
			))
		
		self.cursor.execute("DELETE FROM tags WHERE name = ?", name)

		await interaction.response.send_message(embed=Success(
			title=f"Successfully deleted tag `{name}`"
		))

	@app_commands.command(
		name="list",
		description="List all tags created by you or someone else"
	)
	@app_commands.describe(user="User to list tags of")
	async def _list(self, interaction: Interaction, user: User=None):
		if user == None:
			user = interaction.user

		tags = self.cursor.get_records("SELECT name, uses FROM tags WHERE author = ?", user.id)

		if len(tags) == 0:
			return await interaction.response.send_message(embed=Error(
				title=f"This user doesn't have any tags"
			))

		ordered_list = [f"{i}. {tag.name} ({tag.uses} use{'s'[:tag.uses ^ 1]})" for i, tag in enumerate(tags)]

		embed = Embed(description="\n".join(ordered_list), color=Color.blurple())
		embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)

		await interaction.response.send_message(embed=embed)
	
	@app_commands.command(description="Get info on an existing tag")
	@app_commands.describe(name="The tag's name")
	@app_commands.autocomplete(name=tag_autocomplete)
	async def info(self, interaction: Interaction, name: str):
		tag = self.cursor.get_record("SELECT uses, author, timestamp FROM tags WHERE name = ?", name)

		if tag == None:
			return await interaction.response.send_message(embed=Error(
				title="That tag doesn't exist"
			))

		author = self.bot.get_user(tag.author)

		embed = Embed(
			title=name,
			description=f"**Created by**: <@{author.id}>\n**Uses**: {tag.uses}",
			timestamp=datetime.fromtimestamp(tag.timestamp)
		)

		embed.set_author(name=author.display_name, icon_url=author.display_avatar.url)
		embed.set_footer(text="Tag created at")

		await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
	await bot.add_cog(Tags(bot), guild=DEBUG_GUILD)