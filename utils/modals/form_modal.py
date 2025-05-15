import discord
from discord.ui import View, Button
from utils.modals.evidence_form import ReportActionView
from utils.modals.reject_form import RejectReasonModal
from utils.modals.appeal_form import AppealFormModal
from utils.modals.report_form import ReportFormModal

class FormActionView(View):
    def __init__(self, bot, form_type, db_connection, name=None, ban_reason=None, appeal_reason=None, additional_info=None, report_id=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.form_type = form_type
        self.db_connection = db_connection
        self.name = name
        self.ban_reason = ban_reason
        self.appeal_reason = appeal_reason
        self.additional_info = additional_info
        self.report_id = report_id

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, custom_id="approve_btn")
    async def approve(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.administrator:
            return await self.bot.error_embed(interaction, "You do not have permission to use this command.")
        
        try:
            embed = interaction.message.embeds[0]
            form_type = embed.title.lower()
            report_id = int(embed.footer.text.split("RPT-")[-1])
            if "appeal" in form_type:
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
                cursor.execute(f"UPDATE {table} SET status = %s WHERE {id_col} = %s", ("Approved", report_id))
                cursor.execute(f"SELECT submitted_by FROM {table} WHERE {id_col} = %s", (report_id,))
                user_id = cursor.fetchone()
                cursor.execute(f"SELECT message_id FROM {table} WHERE {id_col} = %s", (report_id,))
                message_id = cursor.fetchone()
            self.db_connection.commit()

            embed.set_field_at(-1, name="Status", value="✅ Approved", inline=False)
            view = ReportActionView(self.bot, interaction.user, db_connection=self.db_connection)
            channel = interaction.guild.get_channel(channel_id)
            message = await channel.fetch_message(message_id[0])
            await message.edit(embed=embed, view=view)
            
            user = await self.bot.fetch_user(user_id[0])
            user_embed = discord.Embed(title=f"{type.capitalize()} Approved", description=f"Your game report `RPT-{report_id}` has been reviewed and processed. The reported user has been moderated." if type == "report" else "Your appeal has been reviewed and approved. Your ban has been lifted.", color=discord.Color.green())
            user_embed.set_footer(text="This is an automated message.")
            await user.send(embed=user_embed)
            await self.bot.success_embed(interaction, "Form has been approved and the user has been notified.")

            if form_type == "appeal":
                appeal_channel_id = self.bot.settings.get("appeals", {}).get("public_appeals_channel")
                appeal_channel = interaction.guild.get_channel(appeal_channel_id)
                if appeal_channel:
                    embed = discord.Embed(title="Ban Appeal Status Update", color=discord.Color.green())
                    embed.add_field(name="Roblox Username", value=self.name, inline=False)
                    embed.add_field(name="Ban Reason", value=self.ban_reason, inline=False)
                    embed.add_field(name="Reason for Appeal", value=self.appeal_reason, inline=False)
                    if self.additional_info:
                        embed.add_field(name="Additional Info", value=self.additional_info, inline=False)
                    embed.add_field(name="Status", value="✅ Approved", inline=False)
                    embed.set_footer(text=f"Submitted by {interaction.user}", icon_url=interaction.user.display_avatar.url)
                    await appeal_channel.send(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger, custom_id="reject_btn")
    async def reject(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.administrator:
            return await self.bot.error_embed(interaction, "You do not have permission to use this command.")
        
        await interaction.response.send_modal(RejectReasonModal(bot=self.bot, db_connection=self.db_connection, name=self.name, ban_reason=self.ban_reason, appeal_reason=self.appeal_reason, additional_info=self.additional_info, report_id=self.report_id))
    
    
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