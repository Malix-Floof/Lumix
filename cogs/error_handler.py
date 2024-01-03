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

import disnake

from disnake.ext import commands
from datetime import datetime

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        channel = self.bot.get_channel(1149329202777170022)
        timestamp = int(datetime.timestamp(datetime.now()))
        command = inter.permissions.value
        name = inter.application_command.name
        embed = disnake.Embed(description=f"`💔` <t:{timestamp}:f> (<t:{timestamp}:R>) Последний вызов вызвал исключение:\n```cmd\n{error}\n```"
                                          f"\nКод разрешений: \n```\n{command}\n```\nСервер: {inter.guild.name}\nПользователь: {inter.author.name}\nID сервера: {inter.guild.id}\nID участника: {inter.author.id}"
                                          f"\n Команда: </{name}:{inter.data.id}>",
                              color=disnake.Colour.red())
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Errors(bot))
