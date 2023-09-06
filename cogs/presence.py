import disnake
from disnake.ext import commands, tasks


class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_stats.start()

    @tasks.loop(minutes=5)
    async def update_stats(self):
        await self.bot.change_presence(activity=disnake.Activity(name=f'за {len(self.bot.guilds)} серверами', type=disnake.ActivityType.watching))


def setup(bot):
    bot.add_cog(Presence(bot))
