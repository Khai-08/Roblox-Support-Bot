import discord
from discord.ui import Modal, TextInput, View, Button
from utils.api_utils import fetch_user_thumbnail_v1, fetch_user_info_v1, fetch_user_thumbnail_v2, fetch_user_info_v2

class ReportFormModal(Modal, title="Game Report Form"):
    def __init__(self, bot, db_connection):
        super().__init__()
        self.bot = bot
        self.form_type = "reports"
        self.db_connection = db_connection

        self.user_id = TextInput(label="Reported Roblox User ID", placeholder="Enter the Roblox User ID", required=True)
        self.reason = TextInput(label="Reason", placeholder="Describe what the player did wrong", style=discord.TextStyle.paragraph, max_length=1024, required=True)
        self.evidence = TextInput(label="Evidence", placeholder="Provide links to images/videos or describe the evidence", style=discord.TextStyle.short, max_length=500, required=True)
        self.additional_info = TextInput(label="Additional Information", style=discord.TextStyle.paragraph, max_length=1024, required=False)

        self.add_item(self.user_id)
        self.add_item(self.reason)
        self.add_item(self.evidence)
        self.add_item(self.additional_info)

    async def on_submit(self, interaction: discord.Interaction):
        settings = self.bot.settings
        pending_channel_id = settings.get(self.form_type, {}).get("pending_reports_channel")

        if not pending_channel_id:
            return await self.bot.error_embed(interaction, "Pending channel not set up. Please contact an admin.")

        pending_channel = interaction.guild.get_channel(pending_channel_id)
        if not pending_channel:
            return await self.bot.error_embed(interaction, "Pending channel is invalid or missing.")

        user_id_input = self.user_id.value.strip()
        if user_id_input.isdigit():
            user_id = int(user_id_input)
        else:
            return await self.bot.error_embed(interaction, "Invalid Roblox User ID. Please enter a valid numeric User ID.")
        
        user_info = await fetch_user_info_v2(user_id)
        if not user_info:
            return await self.bot.error_embed(interaction, "Failed to fetch user info. Please ensure the User ID is correct and exists.")

        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO game_reports (exploiter_id, reason, evidence, additional_info, status, submitted_by, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s, NOW())",
                    (self.user_id.value, self.reason.value, self.evidence.value, self.additional_info.value or "N/A", "Waiting for admin/staff response...", str(interaction.user))
                )
            self.db_connection.commit()
            appeal_id = cursor.lastrowid
            await self.bot.success_embed(interaction, "Your report has been submitted.")
        
            embed = discord.Embed(title="New Game Report", color=discord.Color.blue())
            embed.add_field(name="Roblox Username", value=f"[{user_info['displayName']} (@{user_info['name']})](https://www.roblox.com/users/{user_info['id']}/profile)", inline=False)
            embed.add_field(name="Reason", value=self.reason.value, inline=False)
            embed.add_field(name="Evidence", value=self.evidence.value, inline=False)
            if self.additional_info.value:
                embed.add_field(name="Additional Info", value=self.additional_info.value, inline=False)
            embed.add_field(name="Status", value="Waiting for admin/staff response...", inline=False)
            embed.set_footer(text=f"Submitted by {interaction.user} | RPT-{appeal_id}", icon_url=interaction.user.display_avatar.url)
            embed.set_thumbnail(url=await fetch_user_thumbnail_v2(self.user_id.value))

            view = FormActionView(self.bot, interaction.user, "report", db_connection=self.db_connection, report_id=appeal_id)
            sent_message = await pending_channel.send(embed=embed, view=view)
            view.message = sent_message

        except Exception as e:
            await self.bot.error_embed(interaction, f"Error: {e}")


class AppealFormModal(Modal, title="Game Appeal Form"):
    def __init__(self, bot, db_connection):
        super().__init__()
        self.bot = bot
        self.form_type = "appeals"
        self.db_connection = db_connection

        self.user_id = TextInput(label="Roblox User ID", required=True)
        self.ban_reason = TextInput(label="Ban Reason", style=discord.TextStyle.short, max_length=50, required=True)
        self.appeal_reason = TextInput(label="Reason For Appeal", style=discord.TextStyle.paragraph, max_length=1024, required=True)
        self.additional_info = TextInput(label="Additional Information", style=discord.TextStyle.paragraph, max_length=1024, required=False)

        self.add_item(self.user_id)
        self.add_item(self.ban_reason)
        self.add_item(self.appeal_reason)
        self.add_item(self.additional_info)

    async def on_submit(self, interaction: discord.Interaction):
        settings = self.bot.settings
        pending_channel_id = settings.get(self.form_type, {}).get("pending_appeals_channel")

        if not pending_channel_id:
            return await self.bot.error_embed(interaction, "Pending channel not set up. Please contact an admin.")

        pending_channel = interaction.guild.get_channel(pending_channel_id)
        if not pending_channel:
            return await self.bot.error_embed(interaction, "Pending channel is invalid or missing.")
        
        user_id_input = self.user_id.value.strip()
        if user_id_input.isdigit():
            user_id = int(user_id_input)
        else:
            return await self.bot.error_embed(interaction, "Invalid Roblox User ID. Please enter a valid numeric User ID.")
        
        user_info = await fetch_user_info_v2(user_id)
        if not user_info:
            return await self.bot.error_embed(interaction, "Failed to fetch user info. Please ensure the User ID is correct and exists.")

        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO game_appeals (exploiter_id, ban_reason, appeal_reason, additional_info, status, submitted_by, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s, NOW())",
                    (self.user_id.value, self.ban_reason.value, self.appeal_reason.value, self.additional_info.value or "N/A", "Waiting for admin/staff response...", str(interaction.user))
                )
            self.db_connection.commit()
            appeal_id = cursor.lastrowid
            await self.bot.success_embed(interaction, "Your appeal has been submitted.")

            embed = discord.Embed(title="New Appeal Report", color=discord.Color.blue())
            embed.add_field(name="Roblox Username", value=f"[{user_info['displayName']} (@{user_info['name']})](https://www.roblox.com/users/{user_info['id']}/profile)", inline=False)
            embed.add_field(name="Ban Reason", value=self.ban_reason.value, inline=False)
            embed.add_field(name="Reason For Appeal", value=self.appeal_reason.value, inline=False)
            if self.additional_info.value:
                embed.add_field(name="Additional Info", value=self.additional_info.value, inline=False)
            embed.add_field(name="Status", value="Waiting for admin/staff response...", inline=False)
            embed.set_footer(text=f"Submitted by {interaction.user} | RPT-{appeal_id}", icon_url=interaction.user.display_avatar.url)
            embed.set_thumbnail(url=await fetch_user_thumbnail_v2(self.user_id.value))

            view = FormActionView(self.bot, interaction.user, "appeal", db_connection=self.db_connection, name=user_info["name"], ban_reason=self.ban_reason.value, appeal_reason=self.appeal_reason.value, additional_info=self.additional_info.value, report_id=appeal_id)
            sent_message = await pending_channel.send(embed=embed, view=view)
            view.message = sent_message

        except Exception as e:
            await self.bot.error_embed(interaction, f"Error: {e}")


class RejectReasonModal(Modal, title="Rejection Reason"):
    def __init__(self, bot, user, form_type, db_connection, message, name, ban_reason, appeal_reason, additional_info=None, report_id=None):
        super().__init__()
        self.bot = bot
        self.user = user
        self.form_type = form_type
        self.db_connection = db_connection
        self.message = message
        self.name = name
        self.ban_reason = ban_reason
        self.appeal_reason = appeal_reason
        self.additional_info = additional_info
        self.report_id = report_id
        self.reason = TextInput(label="Reason for Rejection", style=discord.TextStyle.paragraph, required=True)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            with self.db_connection.cursor() as cursor:
                if self.form_type == "report":
                    cursor.execute("UPDATE game_reports SET status = %s WHERE report_id = %s", ("Rejected", self.report_id))
                elif self.form_type == "appeal":
                    cursor.execute("UPDATE game_appeals SET status = %s WHERE appeal_id = %s", ("Rejected", self.report_id))
            self.db_connection.commit()

            embed = self.message.embeds[0]
            embed.set_field_at(-1, name="Status", value=f"❌ Rejected: {self.reason}", inline=False)
            await self.message.edit(embed=embed, view=None)

            user_embed = discord.Embed(title=f"{self.form_type.capitalize()} Rejected", description=("Your game report has been reviewed and no action has been taken." "The report did not meet our moderation criteria." if self.form_type == "report" else "Your appeal has been reviewed and denied. The ban will remain in place."), color=discord.Color.red())
            user_embed.add_field(name="Reason", value=self.reason.value, inline=False)
            user_embed.set_footer(text="This is an automated message.")
            await self.user.send(embed=user_embed)
            await self.bot.success_embed(interaction, "Rejection submitted. The user has been notified.")

            if self.form_type == "appeal":
                channel_id = self.bot.settings.get("appeals", {}).get("public_appeals_channel")
                channel = interaction.guild.get_channel(channel_id) if channel_id else None
                if channel:
                    embed = discord.Embed(title="Ban Appeal Status Update", color=discord.Color.red())
                    embed.add_field(name="Roblox Username", value=self.name, inline=False)
                    embed.add_field(name="Ban Reason", value=self.ban_reason, inline=False)
                    embed.add_field(name="Reason for Appeal", value=self.appeal_reason, inline=False)
                    if self.additional_info:
                        embed.add_field(name="Additional Info", value=self.additional_info, inline=False)
                    embed.add_field(name="Status", value=f"❌ Rejected: {self.reason.value}", inline=False)
                    embed.set_footer(text=f"Submitted by {interaction.user}", icon_url=interaction.user.display_avatar.url)
                    await channel.send(embed=embed)

        except Exception as e:
            await self.bot.error_embed(interaction, f"Error: {e}")


class FormActionView(View):
    def __init__(self, bot, user, form_type, db_connection, name=None, ban_reason=None, appeal_reason=None, additional_info=None, report_id=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.form_type = form_type
        self.db_connection = db_connection
        self.name = name
        self.ban_reason = ban_reason
        self.appeal_reason = appeal_reason
        self.additional_info = additional_info
        self.report_id = report_id
        self.message = None

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, custom_id="approve_btn")
    async def approve(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.administrator:
            return await self.bot.error_embed(interaction, "You do not have permission to use this command.")
        
        try:            
            embed = interaction.message.embeds[0]
            form_type = embed.title.lower()
            report_id = int(embed.footer.text.split("RPT-")[-1])
            user_id = int(embed.footer.text.split("User: ")[-1])

            table = "game_reports" if "report" in form_type else "game_appeals"
            id_col = "report_id" if "report" in form_type else "appeal_id"

            with self.db_connection.cursor() as cursor:
                cursor.execute(f"UPDATE {table} SET status = %s WHERE {id_col} = %s", ("Approved", report_id))
            self.db_connection.commit()

            embed.set_field_at(-1, name="Status", value="✅ Approved", inline=False)
            await self.message.edit(embed=embed, view=None)
            
            user = await self.bot.fetch_user(user_id)
            dm_embed = discord.Embed(title=f"{self.form_type.capitalize()} Approved", description="Your game report has been reviewed and processed. The reported user has been moderated." if self.form_type == "report" else "Your appeal has been reviewed and approved. Your ban has been lifted.", color=discord.Color.green())
            dm_embed.set_footer(text="This is an automated message.")
            await user.send(embed=dm_embed)
            await self.bot.success_embed(interaction, "Form has been approved and the user has been notified.")

            if self.form_type == "appeal":
                channel_id = self.bot.settings.get("appeals", {}).get("public_appeals_channel")
                channel = interaction.guild.get_channel(channel_id) if channel_id else None
                if channel:
                    embed = discord.Embed(title="Ban Appeal Status Update", color=discord.Color.green())
                    embed.add_field(name="Roblox Username", value=self.name, inline=False)
                    embed.add_field(name="Ban Reason", value=self.ban_reason, inline=False)
                    embed.add_field(name="Reason for Appeal", value=self.appeal_reason, inline=False)
                    if self.additional_info:
                        embed.add_field(name="Additional Info", value=self.additional_info, inline=False)
                    embed.add_field(name="Status", value="✅ Approved", inline=False)
                    embed.set_footer(text=f"Submitted by {interaction.user}", icon_url=interaction.user.display_avatar.url)
                    await channel.send(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger, custom_id="reject_btn")
    async def reject(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.administrator:
            return await self.bot.error_embed(interaction, "You do not have permission to use this command.")
        
        await interaction.response.send_modal(RejectReasonModal(bot=self.bot, user=self.user, form_type=self.form_type, db_connection=self.db_connection, message=self.message, name=self.name, ban_reason=self.ban_reason, appeal_reason=self.appeal_reason, additional_info=self.additional_info, report_id=self.report_id))
    
    
class FormButton(discord.ui.Button):
    def __init__(self, form_type):
        super().__init__(label="Create Form", style=discord.ButtonStyle.blurple, custom_id=f"create_form_{form_type}_btn")
        self.form_type = form_type

    async def callback(self, interaction: discord.Interaction):
        view: FormView = self.view
        if not view.bot or not view.form_type:
            return await self.bot.warning_embed(interaction, "Form is not properly configured.")

        if view.form_type == "reports":
            await interaction.response.send_modal(ReportFormModal(bot=view.bot, db_connection=view.db_connection))
        elif view.form_type == "appeals":
            await interaction.response.send_modal(AppealFormModal(bot=view.bot, db_connection=view.db_connection))


class FormView(View):
    def __init__(self, bot, form_type, db_connection):
        super().__init__(timeout=None)
        self.bot = bot
        self.form_type = form_type
        self.db_connection = db_connection
        self.add_item(FormButton(form_type))