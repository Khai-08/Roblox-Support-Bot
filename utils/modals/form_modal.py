import discord
from discord.ui import Modal, TextInput, View, Button

class FormModal(Modal, title="Game Report / Appeal Form"):
    def __init__(self, bot, form_type):
        super().__init__()
        self.bot = bot
        self.form_type = form_type

        self.name = TextInput(label="Reported Player's Roblox Username", placeholder="Enter the exact Roblox username", required=True)
        self.reason = TextInput(label="Reason", placeholder="Describe what the player did wrong", style=discord.TextStyle.paragraph, required=True)
        self.evidence = TextInput(label="Evidence", placeholder="Provide links to images/videos or describe the evidence", style=discord.TextStyle.paragraph, required=True)
        self.additional_info = TextInput(label="Additional Information", style=discord.TextStyle.paragraph, required=False)

        self.add_item(self.name)
        self.add_item(self.reason)
        self.add_item(self.evidence)
        self.add_item(self.additional_info)

    async def on_submit(self, interaction: discord.Interaction):
        settings = self.bot.settings
        pending_channel_id = settings.get(self.form_type, {}).get(f"pending_{self.form_type}_channel")

        if not pending_channel_id:
            error = discord.Embed(description="Pending channel not set up. Please contact an admin.", color=discord.Color.red())
            await interaction.response.send_message(embed=error, ephemeral=True)
            return

        pending_channel = interaction.guild.get_channel(pending_channel_id)
        if not pending_channel:
            error = discord.Embed(description="Pending channel is invalid or missing.", color=discord.Color.red())
            await interaction.response.send_message(embed=error, ephemeral=True)
            return

        embed = discord.Embed(title=f"New {self.form_type.capitalize()} Submission", color=discord.Color.blue())
        embed.add_field(name="Roblox Username", value=self.name.value, inline=False)
        embed.add_field(name="Reason", value=self.reason.value, inline=False)
        embed.add_field(name="Evidence", value=self.evidence.value, inline=False)
        if self.additional_info.value:
            embed.add_field(name="Additional Info", value=self.additional_info.value, inline=False)
        embed.set_footer(text=f"Submitted by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await pending_channel.send(embed=embed)
        await interaction.response.send_message(embed=discord.Embed(description="Your form has been submitted.", color=discord.Color.green()), ephemeral=True)


class FormView(View):
    def __init__(self, bot, form_type):
        super().__init__(timeout=None)
        self.bot = bot
        self.form_type = form_type

    @discord.ui.button(label="Create Form", style=discord.ButtonStyle.blurple)
    async def create_form(self, interaction: discord.Interaction, button: Button):
        if not self.bot or not self.form_type:
            await interaction.response.send_message("Form is not properly configured.", ephemeral=True)
            return
        await interaction.response.send_modal(FormModal(bot=self.bot, form_type=self.form_type))