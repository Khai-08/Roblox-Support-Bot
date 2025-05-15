import discord
from discord.ui import Modal, TextInput
from utils.api_utils import fetch_user_thumbnail_v1, fetch_user_info_v1, fetch_user_thumbnail_v2, fetch_user_info_v2

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
        pending_channel_id = self.bot.settings.get(self.form_type, {}).get("pending_appeals_channel")
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
            cursor.execute("SELECT status FROM game_appeals WHERE exploiter_id = %s ORDER BY created_at DESC LIMIT 1", (user_id,))
            result = cursor.fetchone()
            if result and result[0] == "Approved":
                return await self.bot.error_embed(interaction, "This user has already been moderated. You cannot submit another appeal.")
            elif result and result[0] != "Rejected":
                return await self.bot.error_embed(interaction, "This user already has a pending or active appeal.")
                
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO game_appeals (exploiter_id, ban_reason, appeal_reason, additional_info, status, submitted_by, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s, NOW())",
                    (self.user_id.value, self.ban_reason.value, self.appeal_reason.value, self.additional_info.value or "N/A", "Waiting for admin/staff response...", interaction.user.id)
                )
            appeal_id = cursor.lastrowid
            self.db_connection.commit()
            await self.bot.success_embed(interaction, "Your appeal has been submitted.")

            embed = discord.Embed(title="New Game Appeal", color=discord.Color.blue())
            embed.add_field(name="Roblox Username", value=f"[{user_info['displayName']} (@{user_info['name']})](https://www.roblox.com/users/{user_info['id']}/profile)", inline=False)
            embed.add_field(name="Ban Reason", value=self.ban_reason.value, inline=False)
            embed.add_field(name="Reason For Appeal", value=self.appeal_reason.value, inline=False)
            if self.additional_info.value:
                embed.add_field(name="Additional Info", value=self.additional_info.value, inline=False)
            embed.add_field(name="Status", value="Waiting for admin/staff response...", inline=False)
            embed.set_footer(text=f"Submitted by {interaction.user} | RPT-{appeal_id}", icon_url=interaction.user.display_avatar.url)
            embed.set_thumbnail(url=await fetch_user_thumbnail_v2(self.user_id.value))

            from utils.modals.form_modal import FormActionView
            view = FormActionView(self.bot, "appeal", db_connection=self.db_connection, name=user_info["name"], ban_reason=self.ban_reason.value, appeal_reason=self.appeal_reason.value, additional_info=self.additional_info.value, report_id=appeal_id)
            sent_message = await pending_channel.send(embed=embed, view=view)
            view.message = sent_message

            with self.db_connection.cursor() as cursor:
                cursor.execute("UPDATE game_appeals SET message_id = %s WHERE appeal_id = %s", (sent_message.id, appeal_id))
            self.db_connection.commit()

        except Exception as e:
            await self.bot.error_embed(interaction, f"Error: {e}")