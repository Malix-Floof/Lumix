"""
MIT License

Copyright (c) 2022 - 2024 Tasfers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import aiohttp

from disnake.ext import commands, tasks
from config import settings

class SDCApi(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sdc_stats.start()
        self.session = aiohttp.ClientSession()

    @tasks.loop(minutes=1)
    async def sdc_stats(self):
        headers = {
            'Authorization': settings["sdc_key"],
        }
        data = {
            "servers": len(self.bot.guilds),
            "shards": self.bot.shard_count,
        }
        url = f"https://api.server-discord.com/v2/bots/{self.bot.user.id}/stats"
        async with self.session.post(url, headers=headers, data=data) as resp:
            ...

    @sdc_stats.before_loop
    async def before_sdc_stats(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(SDCApi(bot))
