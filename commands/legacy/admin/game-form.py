import discord
from discord.ext import commands
from discord.ui import Button, Select, View

from utils.config_utils import ConfigurationUtils
from utils.modals.form_modal import FormView

class GameFormDropdown(Select):
    def __init__(self, ctx, form_type, bot, parent_view):
        self.bot, self.ctx = bot, ctx
        self.form_type = form_type
        self.parent_view = parent_view

        options = [discord.SelectOption(label=f"#{channel.name}", value=str(channel.id)) for channel in ctx.guild.text_channels]
        super().__init__(placeholder=f"Select a {form_type} channel...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            error_message = discord.Embed(description="You are not authorized to perform this action.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_message, ephemeral=True)
            return

        selected_channel = discord.utils.get(self.ctx.guild.text_channels, id=int(self.values[0]))
        settings = self.bot.settings
        if self.form_type in settings and isinstance(settings[self.form_type], dict):
            settings[self.form_type][f"{self.form_type}_channel"] = selected_channel.id
        else:
            settings[self.form_type] = {f"{self.form_type}_channel": selected_channel.id}

        ConfigurationUtils.save_config(f"config/settings.{self.bot.bot_config.get('environment').lower()}.json", settings)
        success_embed = discord.Embed(description=f"{self.form_type.capitalize()} form has been successfully linked to {selected_channel.mention}.", color=discord.Color.green())
        for item in self.parent_view.children[:]:
            self.parent_view.remove_item(item)
        await interaction.response.edit_message(embed=success_embed, view=None)

        await self.send_form_embed(selected_channel)
    
    async def send_form_embed(self, channel):
        if self.form_type == "reports":
            embed = discord.Embed(title="Game Report", description="To report a player for in-game misconduct, please press the button below. \n\nInclude as much evidence as possible (e.g., screenshots, videos) to support your report.", color=discord.Color.blue())
        elif self.form_type == "appeals":
            embed = discord.Embed(title="Appeal Request", description="To appeal a punishment, please press the button below. \n\nProvide a clear explanation and any supporting evidence for your appeal.", color=discord.Color.blue())
        embed.set_footer(text="If the button does not work, please inform a Moderator.")

        await channel.send(embed=embed, view=FormView())


def setup(bot):
    @bot.command(name='setup', aliases=['set'])
    @bot.cmd_logger
    @commands.has_permissions(administrator=True)
    async def setup_game_form(ctx):
        try:
            embed = discord.Embed(title="Game Report and Appeal Setup", description="Choose a form type to proceed.", color=discord.Color.blue())
            appeals_button = Button(label="Appeals", style=discord.ButtonStyle.primary, custom_id="appeals_button")
            reports_button = Button(label="Reports", style=discord.ButtonStyle.primary, custom_id="reports_button")
            
            initial_view = View(timeout=30)
            initial_view.add_item(appeals_button)
            initial_view.add_item(reports_button)

            async def button_callback(interaction):
                form_type = interaction.data["custom_id"].replace("_button", "")
                new_embed = discord.Embed(title=f"Select a {form_type.capitalize()} Type", description=f"Please select a {form_type} channel from the list.", color=discord.Color.green())

                channel_select = GameFormDropdown(ctx, form_type, bot, initial_view)
                new_view = View(timeout=30)
                new_view.add_item(channel_select)
                await interaction.response.edit_message(embed=new_embed, view=new_view)

            appeals_button.callback = button_callback
            reports_button.callback = button_callback

            await ctx.reply(embed=embed, view=initial_view, mention_author=False)
        
        except Exception as e:
            await bot.error_embed(ctx, f"An error occurred: {e}")