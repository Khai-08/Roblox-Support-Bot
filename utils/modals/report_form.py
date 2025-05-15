import discord
from discord.ui import Modal, TextInput
from utils.api_utils import fetch_user_thumbnail_v1, fetch_user_info_v1, fetch_user_thumbnail_v2, fetch_user_info_v2

class ReportFormModal(Modal, title="Game Report Form"):
    def __init__(self, bot, db_connection):
        super().__init__()
        self.bot = bot
        self.form_type = "reports"
        self.db_connection = db_connection

        self.user_id = TextInput(label="Reported Roblox User ID", placeholder="Enter the Roblox User ID", required=True)
        self.reason = TextInput(label="Reason", placeholder="Describe what the player did wrong", style=discord.TextStyle.paragraph, max_length=1024, required=True)
        self.evidence = TextInput(label="Evidence", placeholder="Provide links to images/videos or describe the evidence", style=discord.TextStyle.paragraph, max_length=1024, required=True)
        self.additional_info = TextInput(label="Additional Information", style=discord.TextStyle.paragraph, max_length=1024, required=False)

        self.add_item(self.user_id)
        self.add_item(self.reason)
        self.add_item(self.evidence)
        self.add_item(self.additional_info)

    async def on_submit(self, interaction: discord.Interaction):
        pending_channel_id = self.bot.settings.get(self.form_type, {}).get("pending_reports_channel")
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

        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT status FROM game_reports WHERE exploiter_id = %s ORDER BY created_at DESC LIMIT 1", (user_id,))
            existing = cursor.fetchone()
            if existing:
                status = existing[0]
                if status == "Approved":
                    return await self.bot.error_embed(interaction, "This user has already been moderated.")
                elif status != "Rejected":
                    return await self.bot.error_embed(interaction, "This user already has a pending or active report.")   

        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO game_reports (exploiter_id, reason, evidence, additional_info, status, submitted_by, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s, NOW())",
                    (self.user_id.value, self.reason.value, self.evidence.value, self.additional_info.value or "N/A", "Waiting for admin/staff response...", interaction.user.id)
                )
            report_id = cursor.lastrowid
            self.db_connection.commit()
            await self.bot.success_embed(interaction, "Your report has been submitted.")
        
            embed = discord.Embed(title="New Game Report", color=discord.Color.blue())
            embed.add_field(name="Roblox Username", value=f"[{user_info['displayName']} (@{user_info['name']})](https://www.roblox.com/users/{user_info['id']}/profile)", inline=False)
            embed.add_field(name="Reason", value=self.reason.value, inline=False)
            embed.add_field(name="Evidence", value=self.evidence.value, inline=False)
            if self.additional_info.value:
                embed.add_field(name="Additional Info", value=self.additional_info.value, inline=False)
            embed.add_field(name="Status", value="Waiting for admin/staff response...", inline=False)
            embed.set_footer(text=f"Submitted by {interaction.user} | RPT-{report_id}", icon_url=interaction.user.display_avatar.url)
            embed.set_thumbnail(url=await fetch_user_thumbnail_v2(self.user_id.value))

            from utils.modals.form_modal import FormActionView
            view = FormActionView(self.bot, "report", db_connection=self.db_connection, report_id=report_id)
            sent_message = await pending_channel.send(embed=embed, view=view)
            view.message = sent_message

            with self.db_connection.cursor() as cursor:
                cursor.execute("UPDATE game_reports SET message_id = %s WHERE report_id = %s", (sent_message.id, report_id))
            self.db_connection.commit()

        except Exception as e:
            await self.bot.error_embed(interaction, f"Error: {e}")