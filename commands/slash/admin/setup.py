import discord, asyncio
from discord import Interaction, app_commands
from utils.config_utils import ConfigurationUtils
from utils.modals.form_modal import FormView

def setup(bot):
    @bot.tree.command(name="setup", description="Set up channels for reports or appeals.")
    @bot.cmd_logger
    @app_commands.choices(
        type=[
            app_commands.Choice(name="reports", value="reports"),
            app_commands.Choice(name="appeals", value="appeals")
        ]
    )
    @app_commands.describe(form_channel="Select the channel where the form embed will be sent", pending_channel="Select the pending channel to post entries", public_appeals_channel="(Appeals only) Select the public channel where appeals will be posted")
    async def setup(interaction: Interaction, type: app_commands.Choice[str], form_channel: discord.TextChannel, pending_channel: discord.TextChannel, public_appeals_channel: discord.TextChannel = None):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(embed=discord.Embed(description="You do not have permission to use this command.", color=discord.Color.red()), ephemeral=True)
        
        try:
            settings = bot.settings
            settings[type.value] = {
                "form_channel": form_channel.id,
                f"pending_{type.value}_channel": pending_channel.id,
                **({"public_appeals_channel": public_appeals_channel.id} if type.value == "appeals" and public_appeals_channel else {})
            }

            ConfigurationUtils.save_config(f"config/settings.{bot.bot_config.get('environment').lower()}.json", settings)
            success_embed = discord.Embed(description=f"{type.name.capitalize()} system successfully set up. Future submissions will be sent to {pending_channel.mention}.", color=discord.Color.green())
            await interaction.response.send_message(embed=success_embed)

            if type.value == "reports":
                embed = discord.Embed(title="Game Report Form", description="To report a player for in-game misconduct, please press the button below. \n\nInclude as much evidence as possible (e.g., screenshots, videos) to support your report.", color=discord.Color.blue())
            elif type.value == "appeals":
                embed = discord.Embed(title="Game Appeal Form", description="To make an appeal for in-game misconduct, please press the button below. \n\nProvide a clear explanation and any supporting evidence for your appeal.", color=discord.Color.blue())
            else:
                return
            embed.set_footer(text="If the button does not work, please inform a Moderator.")

            form_view = FormView(bot=bot, form_type=type.value, db_connection=bot.db_connection)
            await form_channel.send(embed=embed, view=form_view)

            await asyncio.sleep(5)
            await (await interaction.original_response()).delete()

        except Exception as e:
            await bot.error_embed(interaction, f"An error occurred: {e}")