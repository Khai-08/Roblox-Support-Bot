import discord
from discord.ui import Modal, TextInput, View, Button

class EvidenceSubmissionModal(Modal, title="Submit Updated Evidence"):
    def __init__(self, bot, db_connection, report_id, message):
        super().__init__()
        self.bot = bot
        self.db_connection = db_connection
        self.report_id = report_id
        self.message = message

        self.evidence = TextInput(label="Updated Evidence", placeholder="Provide links to images/videos or describe the updated evidence", style=discord.TextStyle.paragraph, max_length=1024, required=True)
        self.add_item(self.evidence)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("UPDATE game_reports SET evidence = %s WHERE report_id = %s", (self.evidence.value, self.report_id))
            self.db_connection.commit()
            
            user_embed = discord.Embed(title=f"RPT-{self.report_id} Submitted", description="Your updated evidence has been recorded. This helps us maintain proper documentation for the case.", color=discord.Color.green())
            user_embed.set_footer(text="This is an automated message.")
            await self.message.edit(embed=user_embed, view=None)
            await self.bot.success_embed(interaction, "The updated evidence has been submitted successfully.")
        
        except Exception as e:
            await self.bot.error_embed(interaction, f"Failed to process: {e}")


class EvidenceRequestView(View):
    def __init__(self, bot, db_connection):
        super().__init__(timeout=None)
        self.bot = bot
        self.db_connection = db_connection

    @discord.ui.button(label="Request Updated Evidence", style=discord.ButtonStyle.primary, custom_id="evidence_button")
    async def submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        report_id = int(interaction.message.embeds[0].title.split("RPT-")[-1].split()[0])
        modal = EvidenceSubmissionModal(self.bot, self.db_connection, report_id, interaction.message)
        await interaction.response.send_modal(modal)


class ReportActionView(View):
    def __init__(self, bot, user, db_connection):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.db_connection = db_connection

    @discord.ui.button(label="Request Evidence Update", style=discord.ButtonStyle.primary, custom_id="evidence_update")
    async def evidence_update(self, interaction: discord.Interaction, button: Button):
        try:
            report_id = int(interaction.message.embeds[0].footer.text.split("RPT-")[-1].split()[0])
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT submitted_by FROM game_reports WHERE report_id = %s", (report_id,))
                result = cursor.fetchone()
                
            user = await self.bot.fetch_user(result[0])
            user_embed = discord.Embed(title=f"Request for Updated RPT-{report_id} Evidence", description="Hello, we're following up on your previous report. To help us maintain proper records of banned users, we need updated evidence. Please provide it at your earliest convenience.", color=discord.Color.blue())      
            user_embed.set_footer(text="This is an automated message.")
            view = EvidenceRequestView(self.bot, self.db_connection)
            await user.send(embed=user_embed, view=view)
            await self.bot.success_embed(interaction, "User has been notified to provide updated evidence.")

        except Exception as e:
            await self.bot.error_embed(interaction, f"Failed to process: {e}")