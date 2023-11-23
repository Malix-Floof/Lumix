import aiohttp
from disnake.ext import commands, tasks
from config import settings

class SDCApi(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sdc_stats.start()
        self.session = aiohttp.ClientSession()

    @commands.Cog.listener()
    async def on_ready(self):
        print("sdc_api.py is ready!")

    @tasks.loop(minutes=1)
    async def sdc_stats(self):
        headers = {
            'Authorization': settings["sdc_key"],
        }
        data = {
            "servers": len(self.bot.guilds),
            "shards": self.bot.shard_count,
        }
        url = "https://api.server-discord.com/v2/bots/1006946815050006539/stats"
        async with self.session.post(url, headers=headers, data=data) as resp:
            ...

    @sdc_stats.before_loop
    async def before_sdc_stats(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(SDCApi(bot))
