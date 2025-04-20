import discord
from discord.ui import Modal, TextInput, View, Button

class FormModal(Modal, title="Game Report / Appeal Form"):
    name = TextInput(label="Reported Player's Roblox Username", placeholder="Enter the exact Roblox username", required=True)
    reason = TextInput(label="Reason", placeholder="Describe what the player did wrong", style=discord.TextStyle.paragraph, required=True)
    evidence = TextInput(label="Evidence", placeholder="Provide links to images/videos or describe the evidence", style=discord.TextStyle.paragraph, required=True)
    additional_info = TextInput(label="Additional Information", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        confirmation = discord.Embed(description="Your form has been submitted.", color=discord.Color.green())
        await interaction.response.send_message(embed=confirmation, ephemeral=True)
        # Add your form processing logic here (e.g., saving the form data, sending it to a specific channel, etc.)

class FormView(View):
    def __init__(self): 
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Form", style=discord.ButtonStyle.blurple)
    async def create_form(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(FormModal())
