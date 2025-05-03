import discord
from discord.ext import commands
from discord.ui import Button, Select, View

from utils.config_utils import ConfigurationUtils
from utils.modals.form_modal import FormView

class GameFormDropdown(Select):
    def __init__(self, ctx, form_type, bot, parent_view, channel_type):
        self.bot, self.ctx = bot, ctx
        self.form_type = form_type
        self.channel_type = channel_type
        self.parent_view = parent_view

        self.options = [discord.SelectOption(label=f"#{channel.name}", value=str(channel.id)) for channel in ctx.guild.text_channels]
        self.placeholder = f"Select a {channel_type} channel for {form_type}..."
        super().__init__(placeholder=self.placeholder, options=self.options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to perform this action.", color=discord.Color.red()), ephemeral=True)
            return

        selected_channel = discord.utils.get(self.ctx.guild.text_channels, id=int(self.values[0]))
        settings = self.bot.settings

        if self.form_type not in settings or not isinstance(settings[self.form_type], dict):
            settings[self.form_type] = {}

        settings[self.form_type][f"{self.channel_type}_{self.form_type}_channel"] = selected_channel.id
        ConfigurationUtils.save_config(f"config/settings.{self.bot.bot_config.get('environment').lower()}.json", settings)

        success_embed = discord.Embed(description=f"**{self.form_type.capitalize()}** {self.channel_type} channel set to {selected_channel.mention}.", color=discord.Color.green())
        for item in self.parent_view.children[:]:
            self.parent_view.remove_item(item)
        await interaction.response.edit_message(embed=success_embed, view=None)

        if self.channel_type == "form":
            await self.send_form_embed(selected_channel)

    async def send_form_embed(self, channel):
        if self.form_type == "reports":
            embed = discord.Embed(title="Game Report", description="To report a player for in-game misconduct, please press the button below. \n\nInclude as much evidence as possible (e.g., screenshots, videos) to support your report.", color=discord.Color.blue())
        elif self.form_type == "appeals":
            embed = discord.Embed(title="Appeal Request", description="To appeal a punishment, please press the button below. \n\nProvide a clear explanation and any supporting evidence for your appeal.", color=discord.Color.blue())
        else:
            return
        embed.set_footer(text="If the button does not work, please inform a Moderator.")

        await channel.send(embed=embed, view=FormView(bot=self.bot, form_type=self.form_type))


def setup(bot):
    @bot.command(name='setup', aliases=['set'])
    @bot.cmd_logger
    @commands.has_permissions(administrator=True)
    async def setup_game_form(ctx):
        try:
            embed = discord.Embed(title="Game Report and Appeal Setup", description="Choose a form type to configure.", color=discord.Color.blue())
            appeals_button = Button(label="Appeals", style=discord.ButtonStyle.primary, custom_id="appeals_button")
            reports_button = Button(label="Reports", style=discord.ButtonStyle.primary, custom_id="reports_button")

            initial_view = View(timeout=30)
            initial_view.add_item(appeals_button)
            initial_view.add_item(reports_button)

            async def button_callback(interaction):
                form_type = "reports" if interaction.data["custom_id"] == "reports_button" else "appeals"
                form_embed = discord.Embed(title=f"Select {form_type.capitalize()} Form Channel", description="Select the channel where the form button will be posted.", color=discord.Color.green())
                form_view = View(timeout=30)
                form_view.add_item(GameFormDropdown(ctx, form_type, bot, form_view, "form"))
                await interaction.response.edit_message(embed=form_embed, view=form_view)

                def form_check(i): return i.user == ctx.author and i.message.id == interaction.message.id
                await bot.wait_for("interaction", check=form_check, timeout=30)

                pending_embed = discord.Embed(title=f"Select Pending {form_type.capitalize()} Channel", description="Select the channel where submitted entries will appear.", color=discord.Color.orange())
                pending_view = View(timeout=30)
                pending_view.add_item(GameFormDropdown(ctx, form_type, bot, pending_view, "pending"))
                await interaction.edit_original_response(embed=pending_embed, view=pending_view)

            appeals_button.callback = button_callback
            reports_button.callback = button_callback

            await ctx.reply(embed=embed, view=initial_view, mention_author=False)

        except Exception as e:
            await bot.error_embed(ctx, f"An error occurred: {e}")