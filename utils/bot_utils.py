class BotFunctions:
    def __init__(self, bot):
        self.bot = bot

    def sync_commands(self, guild_id: int, command_name: str) -> bool:
        guild_id_str = str(guild_id)
        if guild_id_str not in self.global_settings:
            return False
        command_states = self.global_settings[guild_id_str].get("command_states", {})
        return command_states.get(command_name, False)