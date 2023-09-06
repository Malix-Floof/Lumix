import aiohttp
from disnake.ext import commands, tasks
from config import settings
import logging

log = logging.getLogger("SDC.connect")


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
            "shards": 1,
        }
        url = "https://api.server-discord.com/v2/bots/1006946815050006539/stats"
        async with self.session.post(url, headers=headers, data=data) as resp:
            status = resp.status
            if status == 200:
                log.info("Статистика на SDC обновлена! Статус 200")
            if status == 404:
                log.info("[ ERR ] Не удалось обновить статистику на SDC!")
            if status == 429:
                log.info("[ ERR ] Слишком частые запросы на SDC!")

    @sdc_stats.before_loop
    async def before_sdc_stats(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(SDCApi(bot))