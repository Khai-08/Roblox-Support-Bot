import discord
from discord.ui import Modal, TextInput

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