import discord
from discord.ui import Button, View

class GuildPaginator(View):
    def __init__(self, bot, interaction, guild_names, per_page=10):
        super().__init__()
        self.bot = bot
        self.interaction = interaction
        self.guild_names = guild_names
        self.per_page = per_page
        self.current_page = 0
        self.total_pages = (len(guild_names) - 1) // per_page + 1
        self.author_id = interaction.user.id

        self.prev_button = Button(label="◀", style=discord.ButtonStyle.primary, disabled=True)
        self.next_button = Button(label="▶", style=discord.ButtonStyle.primary, disabled=self.total_pages <= 1)
        
        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page
        
        self.add_item(self.prev_button)
        self.add_item(self.next_button)
    
    async def update_buttons(self, interaction):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= self.total_pages - 1
        await interaction.response.edit_message(embed=self.get_embed(), view=self)
    
    def get_embed(self):
        total_bots = sum(1 for guild in self.bot.guilds for member in guild.members if member.bot)
        total_members = sum(guild.member_count for guild in self.bot.guilds)
        total_humans = total_members - total_bots

        start = self.current_page * self.per_page
        end = start + self.per_page
        guilds_page = self.guild_names[start:end]

        embed = discord.Embed(title="Bot Analytics", color=self.bot.embed_color)
        embed.add_field(name="Total Servers (Guilds)", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="Total Members", value=f"{total_members}", inline=True)
        embed.add_field(name="Total Bots", value=f"{total_bots}", inline=True)
        embed.add_field(name="Total Humans", value=f"{total_humans}", inline=True)
        embed.add_field(name="Guild Names", value="\n".join(guilds_page), inline=False)
        embed.add_field(name="\u200b", value=f"-# **Page {self.current_page + 1} / {self.total_pages}**", inline=False)
        embed.set_footer(text=self.bot.footer_text, icon_url=self.bot.user.avatar.replace(format='png'))
        embed.set_thumbnail(url=self.bot.user.avatar.replace(format='png'))
        return embed
    
    async def prev_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            error_message = discord.Embed(description="You are not the author to perform this action.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_message, ephemeral=True)
            return
        self.current_page -= 1
        await self.update_buttons(interaction)
    
    async def next_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            error_message = discord.Embed(description="You are not the author to perform this action.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_message, ephemeral=True)
            return
        self.current_page += 1
        await self.update_buttons(interaction)    

def setup(bot):
    @bot.tree.command(name="analytics", description="Displays bot analytics including server count and member information. (Owner-only)")
    @bot.cmd_logger
    async def analytics_command(interaction: discord.Interaction):
        if interaction.user.id != bot.owner:
            return await bot.error_embed(interaction, "You must be the bot owner to use this command. Only the owner can execute this command.")
    
        try:
            total_guilds = len(bot.guilds)
            total_members = sum(guild.member_count for guild in bot.guilds)
            total_bots = sum(1 for guild in bot.guilds for member in guild.members if member.bot)
            total_humans = total_members - total_bots

            guild_names = [f"{i + 1}. {guild.name}" for i, guild in enumerate(sorted(bot.guilds, key=lambda g: g.me.joined_at, reverse=True))]

            embed = discord.Embed(title="Bot Analytics", color=bot.embed_color)
            embed.add_field(name="Total Servers (Guilds)", value=f"{total_guilds}", inline=True)
            embed.add_field(name="Total Members", value=f"{total_members}", inline=True)
            embed.add_field(name="Total Bots", value=f"{total_bots}", inline=True)
            embed.add_field(name="Total Humans", value=f"{total_humans}", inline=True)
            embed.set_footer(text=bot.footer_text, icon_url=bot.user.avatar.replace(format='png'))
            embed.set_thumbnail(url=bot.user.avatar.replace(format='png'))

            if len(guild_names) > 10:
                view = GuildPaginator(bot, interaction, guild_names)
                await interaction.response.send_message(embed=view.get_embed(), view=view, ephemeral=False)
            else:
                embed.add_field(name="Guild Names", value="\n".join(guild_names), inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=False)

        except Exception as e:
            await bot.error_embed(interaction, f"An error occurred: {e}")