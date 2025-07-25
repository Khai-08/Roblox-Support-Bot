import os, sys, time, discord, importlib.util

from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
from functools import wraps

from utils.config_utils import ConfigurationUtils
from utils.modals.evidence_form import EvidenceRequestView, ReportActionView
from utils.modals.form_modal import FormActionView, FormView
from config.db_config import get_db_connection

class FISCHBot(commands.Bot):
    def __init__(self):
        load_dotenv()
        self.bot_token = os.getenv("BOT_TOKEN")
        if not self.bot_token:
            raise ValueError("BOT_TOKEN not found in environment variables. Please ensure it is set in the .env file.")
        
        self.bot_config = ConfigurationUtils.load_config(os.path.join('config', 'bot_config.json'))
        settings_file = f"config/settings.{self.bot_config.get('environment').lower()}.json"
        if not os.path.exists(settings_file):
            print(f"Settings file {settings_file} is missing. Creating default settings file.")
            ConfigurationUtils.default_settings(settings_file)
        self.settings = ConfigurationUtils.load_config(settings_file)
        self.db_connection = get_db_connection(self.settings)

        self.embed_color = discord.Color.from_rgb(255, 164, 188)
        self.footer_text = self.bot_config.get("footer_text")
        self.bot_stat = self.bot_config.get('bot_stat', {})
        self.presence = self.bot_stat.get("presence")
        self.owner = self.bot_config.get("owner_id")
        self.stat = self.bot_stat.get("status")
        
        super().__init__(command_prefix="!",intents=discord.Intents.all(), help_command=None)

        self.config_functions = ConfigurationUtils(self)
        self.setup_commands(self)

    def setup_commands(self, bot):
        self.load_commands('commands/slash', bot)

    def load_commands(self, folder_path, bot):
        for dirpath, __, filenames in os.walk(folder_path):
            for file_name in filenames:
                if file_name.endswith('.py'):
                    file_path = os.path.join(dirpath, file_name)
                    module_name = file_path.replace(os.sep, '.')[:-3]
                    module_spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(module_spec)
                    sys.modules[module_name] = module
                    module_spec.loader.exec_module(module)

                    if hasattr(module, 'setup'):
                        module.setup(bot)
                    else:
                        print(f"Warning: The module {module_name} does not have a setup function.")

    def run(self):
        super().run(self.bot_token, reconnect=True)

    ## DECORATOR
    @staticmethod
    def cmd_logger(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            try:
                if isinstance(ctx, discord.ext.commands.Context):
                    await func(ctx, *args, **kwargs)
                    print(f"[{timestamp}] | SUCCESS | {ctx.author} used `{ctx.command}` in {ctx.guild.name}")
                elif isinstance(ctx, discord.Interaction):
                    await func(ctx, *args, **kwargs)
                    print(f"[{timestamp}] | SUCCESS | {ctx.user} used `{ctx.command.name}` in {ctx.guild.name}")
                    
            except Exception as e:
                if isinstance(ctx, discord.ext.commands.Context):
                    print(f"[{timestamp}] | FAILED | {ctx.author} used `{ctx.command}` in {ctx.guild.name}: {e}")
                elif isinstance(ctx, discord.Interaction):
                    print(f"[{timestamp}] | FAILED | {ctx.user} used `{ctx.command.name}` in {ctx.guild.name}: {e}")
                    
        return wrapper
    
    ## UTILS    
    async def send_embed(self, ctx_or_interaction, message: str, color: discord.Color):
        embed = discord.Embed(description=message, color=color)
        if isinstance(ctx_or_interaction, discord.Interaction):
            if not ctx_or_interaction.response.is_done():
                await ctx_or_interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await ctx_or_interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await ctx_or_interaction.reply(embed=embed, mention_author=False)

    async def success_embed(self, ctx_or_interaction, message: str):
        await self.send_embed(ctx_or_interaction, message, discord.Color.green())

    async def warning_embed(self, ctx_or_interaction, message: str):
        await self.send_embed(ctx_or_interaction, message, discord.Color.orange())

    async def error_embed(self, ctx_or_interaction, message: str):
        await self.send_embed(ctx_or_interaction, message, discord.Color.red())

    async def on_ready(self):
        presence_mapping = {
            'playing': discord.ActivityType.playing,
            'listening': discord.ActivityType.listening,
            'watching': discord.ActivityType.watching,
            'streaming': discord.ActivityType.streaming
        }.get(self.presence.lower(), discord.ActivityType.playing)
        await self.change_presence(activity=discord.Activity(type=presence_mapping, name=self.stat))

        bot.add_view(ReportActionView(bot, None, self.db_connection))
        bot.add_view(FormActionView(bot, None, self.db_connection))
        bot.add_view(EvidenceRequestView(bot, self.db_connection))
        bot.add_view(FormView(bot, "appeals", self.db_connection))
        bot.add_view(FormView(bot, "reports", self.db_connection))

        self.start_time = time.time()
        await bot.tree.sync()

bot = FISCHBot()

@bot.event
async def on_message(message):
    if message.author != bot.user and bot.user.mentioned_in(message):
        embed = discord.Embed(description="Encountered any issues or bugs? Please DM <@775966789950505002>", color=bot.embed_color)
        embed.set_footer(text=bot.footer_text, icon_url=bot.user.avatar.url)
        await message.channel.send(embed=embed)
    await bot.process_commands(message)


# Global Slash Command Error Handler 
@bot.tree.error
async def on_slash_command_error(interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await bot.error_embed(interaction, "You do not have permission to use this command.")

    elif isinstance(error, app_commands.errors.MissingRole):
        await bot.error_embed(interaction, "You do not have the required role to run this command.")


bot.run()