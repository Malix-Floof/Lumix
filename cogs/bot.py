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

import psutil
import disnake

from disnake.ext import commands
from config import settings
from platform import python_version
from humanize import naturalsize
from datetime import datetime
from os import getpid
from db import SQLITE

db = SQLITE("database.db")

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="📌 Показывает статистику бота")
    async def bot(self, inter):
        await inter.response.defer()
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        devs = "`malix.floof`, `towux`"
        servers = len(self.bot.guilds)
        users = len(self.bot.users)
        cpu = psutil.cpu_percent()
        ram = naturalsize(psutil.Process(getpid()).memory_info().rss)
        total_ram = naturalsize(psutil.virtual_memory().total)
        pyver = python_version()
        ping = round(self.bot.latency * 1000)
        buttons = disnake.ui.View()
        if lang_server == 'ru':
            website = "Сайт"
            support = "Сервер поддержки"
            embed = disnake.Embed(
                title=f"Статистика бота",
                description=f"**Разработчики:** {devs}\n **Ваш сервер расположен на осколке: `#{inter.guild.shard_id}/{self.bot.shard_count}`**\n"
                        "\n`✨` **Основная статистика:**\n"
                        f"Серверов: **{servers}**\n"
                        f"Пользователи: **{users}**\n\n"
                        "`🤖` **Платформа:**\n"
                        f"Нагрузка: **{cpu}%**\n"
                        f"ОЗУ: **{ram} / {total_ram}**\n"
                        f"Задержка: **{ping}ms**\n\n"
                        "`🔧` **Конфигурация:** \n"
                        f"Версия python: **{pyver}**\n"
                        f"Библиотека: **Disnake {disnake.__version__}**\n\n"
                        f"Запущено <t:{settings['uptime']}:R>",
                color=0x2b2d31)
            embed.set_footer(text=f"Tasfers © Copyright 2022  -  {datetime.today().year}  ・  Все права защищены")
        if lang_server == 'en':
            website = "Website"
            support = "Support server"
            embed = disnake.Embed(
                title=f"Bot statistics",
                description=f"**Developers:** {devs}\n **Your server is located on a shard: `#{inter.guild.shard_id}/{self.bot.shard_count}`**\n"
                        "\n`✨` **Basic Statistics:**\n"
                        f"Servers: **{servers}**\n"
                        f"Users: **{users}**\n"
                        "`🤖` **Platform:**\n"
                        f"CPU: **{cpu}%**\n"
                        f"RAM: **{ram} / {total_ram}**\n"
                        f"Ping: **{ping}ms**\n\n"
                        "`🔧` **Configuration:**\n"
                        f"Python version: **{pyver}**\n"
                        f"Library: **Disnake {disnake.__version__}**\n\n"
                        f"Launched <t:{settings['uptime']}:R>",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Tasfers © Copyright 2022  -  {datetime.today().year}  ・  All rights reserved")
        if lang_server == 'uk':
            website = "Сайт"
            support = "Сервер підтримки"
            embed = disnake.Embed(
                title=f"Статистика",
                description=f"**Розробники:** {devs}\n **Ваш сервер розташований на осколку: `#{inter.guild.shard_id}/{self.bot.shard_count}`**\n"
                        "\n`✨` **Основна статистика:**\n"
                        f"Серверів: **{servers}**\n"
                        f"Користувачі: **{users}**\n"
                        "`🤖` **Платформа:**\n"
                        f"Навантаження: **{cpu}%**\n"
                        f"ОЗУ: **{ram} / {total_ram}**\n"
                        f"Затримка: **{round(self.bot.latency * 1000)}ms**\n\n"
                        "`🔧` **Конфігурація:** \n"
                        f"Версія python: **{pyver}**\n"
                        f"Бібліотека: **Disnake {disnake.__version__}**\n\n"
                        f"Запущено <t:{settings['uptime']}:R>", color=0x2b2d31)
            embed.set_footer(text=f"Tasfers © Copyright 2022  -  {datetime.today().year}  ・  Всі права захищені")
        buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.link, label="SD.C", url="https://bots.server-discord.com/1006946815050006539"))
        buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.link, label="Boticord", url="https://boticord.top/bot/1006946815050006539"))
        buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.link, label=website, url="https://lumix.tasfers.com"))
        buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.link, label=support, url="https://discord.gg/SpTBwz4xsa"))
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1151406452611751936/1178282316150341732/imgonline-com-ua-Shape-sw0GAiNnWm6RPvB6.png')
        await inter.edit_original_message(embed=embed, view=buttons)


def setup(bot):
    bot.add_cog(Information(bot))
