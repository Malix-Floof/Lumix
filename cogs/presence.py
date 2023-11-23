import disnake
from disnake.ext import commands, tasks

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.update_stats.start()

    @tasks.loop(minutes=1)
    async def update_stats(self):
        servers = len(self.bot.guilds)
        serverstr = (
            str(servers) if servers < 1000
            else f'{round(servers / 1000, 1)}k' if servers < 1000000
            else f'{round(servers / 1000000, 1)}M'
        )
        await self.bot.change_presence(activity=disnake.Activity(name=f'за {serverstr} серверами', type=disnake.ActivityType.watching))

def setup(bot):
    bot.add_cog(Presence(bot))
