import discord
from discord.ui import Modal, TextInput

class RejectReasonModal(Modal, title="Rejection Reason"):
    def __init__(self, bot, db_connection, name, ban_reason, appeal_reason, additional_info=None, report_id=None):
        super().__init__()
        self.bot = bot
        self.db_connection = db_connection
        self.name = name
        self.ban_reason = ban_reason
        self.appeal_reason = appeal_reason
        self.additional_info = additional_info
        self.report_id = report_id
        self.reason = TextInput(label="Reason for Rejection", style=discord.TextStyle.paragraph, required=True)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            embed = interaction.message.embeds[0]
            form_type = embed.title.lower()
            report_id = int(embed.footer.text.split("RPT-")[-1])
            if "appeal" in form_type.lower():
                channel_id = self.bot.settings.get("appeals", {}).get("pending_appeals_channel")
                table = "game_appeals"
                id_col = "appeal_id"
                type = "appeal"
            else:
                channel_id = self.bot.settings.get("reports", {}).get("pending_reports_channel")
                table = "game_reports"
                id_col = "report_id"
                type = "report"

            with self.db_connection.cursor() as cursor:
                cursor.execute(f"UPDATE {table} SET status = %s WHERE {id_col} = %s", ("Rejected", report_id))
                cursor.execute(f"SELECT submitted_by FROM {table} WHERE {id_col} = %s", (report_id,))
                user_id = cursor.fetchone()
                cursor.execute(f"SELECT message_id FROM {table} WHERE {id_col} = %s", (report_id,))
                message_id = cursor.fetchone()                
            self.db_connection.commit()
            
            embed.set_field_at(-1, name="Status", value=f"❌ Rejected: {self.reason}", inline=False)
            channel = interaction.guild.get_channel(channel_id)
            message = await channel.fetch_message(message_id[0])
            await message.edit(embed=embed, view=None)
            
            user = await self.bot.fetch_user(user_id[0])
            user_embed = discord.Embed(title=f"{type.capitalize()} Rejected", description=("Your game report has been reviewed and no action has been taken. The report did not meet our moderation criteria." if type == "report" else "Your appeal has been reviewed and denied. The ban will remain in place."), color=discord.Color.red())
            user_embed.add_field(name="Reason", value=self.reason.value, inline=False)
            user_embed.set_footer(text="This is an automated message.")
            await user.send(embed=user_embed)
            await self.bot.success_embed(interaction, "Rejection submitted. The user has been notified.")

            if form_type == "appeal":
                appeal_channel_id = self.bot.settings.get("appeals", {}).get("public_appeals_channel")
                appeal_channel = interaction.guild.get_channel(appeal_channel_id)
                if appeal_channel:
                    embed = discord.Embed(title="Ban Appeal Status Update", color=discord.Color.red())
                    embed.add_field(name="Roblox Username", value=self.name, inline=False)
                    embed.add_field(name="Ban Reason", value=self.ban_reason, inline=False)
                    embed.add_field(name="Reason for Appeal", value=self.appeal_reason, inline=False)
                    if self.additional_info:
                        embed.add_field(name="Additional Info", value=self.additional_info, inline=False)
                    embed.add_field(name="Status", value=f"❌ Rejected: {self.reason.value}", inline=False)
                    embed.set_footer(text=f"Submitted by {interaction.user}", icon_url=interaction.user.display_avatar.url)
                    await appeal_channel.send(embed=embed)

        except Exception as e:
            await self.bot.error_embed(interaction, f"Error: {e}")