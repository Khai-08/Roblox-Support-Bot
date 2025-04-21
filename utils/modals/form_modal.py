import discord
from discord.ui import Modal, TextInput, View, Button

class ReportFormModal(Modal, title="Game Report Form"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.form_type = "reports"

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
        pending_channel_id = settings.get(self.form_type, {}).get("pending_reports_channel")

        if not pending_channel_id:
            await interaction.response.send_message(embed=discord.Embed(description="Pending channel not set up. Please contact an admin.", color=discord.Color.red()), ephemeral=True)
            return

        pending_channel = interaction.guild.get_channel(pending_channel_id)
        if not pending_channel:
            await interaction.response.send_message(embed=discord.Embed(description="Pending channel is invalid or missing.", color=discord.Color.red()), ephemeral=True)
            return

        embed = discord.Embed(title="New Game Report", color=discord.Color.blue())
        embed.add_field(name="Roblox Username", value=self.name.value, inline=False)
        embed.add_field(name="Reason", value=self.reason.value, inline=False)
        embed.add_field(name="Evidence", value=self.evidence.value, inline=False)
        if self.additional_info.value:
            embed.add_field(name="Additional Info", value=self.additional_info.value, inline=False)
        embed.set_footer(text=f"Submitted by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        view = FormActionView(self.bot, interaction.user, "report")
        await pending_channel.send(embed=embed, view=view)
        await interaction.response.send_message(embed=discord.Embed(description="Your report has been submitted.", color=discord.Color.green()), ephemeral=True)


class AppealFormModal(Modal, title="Appeal Form"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.form_type = "appeals"

        self.name = TextInput(label="Roblox Username", required=True)
        self.ban_reason = TextInput(label="Ban Reason", required=True)
        self.appeal_reason = TextInput(label="Reason For Appeal", style=discord.TextStyle.paragraph, required=True)
        self.additional_info = TextInput(label="Additional Information", style=discord.TextStyle.paragraph, required=False)

        self.add_item(self.name)
        self.add_item(self.ban_reason)
        self.add_item(self.appeal_reason)
        self.add_item(self.additional_info)

    async def on_submit(self, interaction: discord.Interaction):
        settings = self.bot.settings
        pending_channel_id = settings.get(self.form_type, {}).get("pending_appeals_channel")

        if not pending_channel_id:
            await interaction.response.send_message(embed=discord.Embed(description="Pending channel not set up. Please contact an admin.", color=discord.Color.red()), ephemeral=True)
            return

        pending_channel = interaction.guild.get_channel(pending_channel_id)
        if not pending_channel:
            await interaction.response.send_message(embed=discord.Embed(description="Pending channel is invalid or missing.", color=discord.Color.red()), ephemeral=True)
            return

        embed = discord.Embed(title="New Appeal Report", color=discord.Color.blue())
        embed.add_field(name="Roblox Username", value=self.name.value, inline=False)
        embed.add_field(name="Ban Reason", value=self.ban_reason.value, inline=False)
        embed.add_field(name="Reason For Appeal", value=self.appeal_reason.value, inline=False)
        if self.additional_info.value:
            embed.add_field(name="Additional Info", value=self.additional_info.value, inline=False)
        embed.set_footer(text=f"Submitted by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        view = FormActionView(self.bot, interaction.user, "appeal")
        await pending_channel.send(embed=embed, view=view)
        await interaction.response.send_message(embed=discord.Embed(description="Your appeal has been submitted.", color=discord.Color.green()), ephemeral=True)


class RejectReasonModal(Modal, title="Rejection Reason"):
    def __init__(self, bot, user, form_type):
        super().__init__()
        self.bot = bot
        self.user = user
        self.form_type = form_type
        self.reason = TextInput(label="Reason for Rejection", style=discord.TextStyle.paragraph, required=True)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Rejection reason submitted.", ephemeral=True)
        
        embed = discord.Embed(title=f"{self.form_type.capitalize()} Rejected", color=discord.Color.red(), description="Your game report has been reviewed and no action has been taken. The report did not meet our moderation criteria." if self.form_type == "report" else "Your appeal has been reviewed and denied. The ban will remain in place.")
        embed.add_field(name="Reason", value=self.reason.value, inline=False)
        embed.set_footer(text="This is an automated message.")

        try:
            await self.user.send(embed=embed)
        except:
            pass

        await interaction.message.edit(view=None)


class FormActionView(View):
    def __init__(self, bot, user, form_type):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.form_type = form_type

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Form approved.", ephemeral=True)

        embed = discord.Embed(title=f"{self.form_type.capitalize()} Approved", color=discord.Color.green(), description="Your game report has been reviewed and processed. The reported user has been moderated." if self.form_type == "report" else "Your appeal has been reviewed and approved. Your ban has been lifted.")
        embed.set_footer(text="This is an automated message.")

        try:
            await self.user.send(embed=embed)
        except:
            pass

        await interaction.message.edit(view=None)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RejectReasonModal(bot=self.bot, user=self.user, form_type=self.form_type))


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

        if self.form_type == "reports":
            await interaction.response.send_modal(ReportFormModal(bot=self.bot))
        elif self.form_type == "appeals":
            await interaction.response.send_modal(AppealFormModal(bot=self.bot))