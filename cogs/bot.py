import disnake
from disnake.ext import commands
from config import settings
import time
import psutil
from platform import python_version
from humanize import naturalsize
from datetime import datetime
from os import getpid
from db import SQLITE

db = SQLITE("database.db")

class Information(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
       
    time = time.time()

    @commands.Cog.listener()
    async def on_ready(self):
        print("bot.py is ready")

    @commands.slash_command(description="📌 Информация | Показывает статистику бота")
    async def bot(self, inter):
        await inter.response.defer()
        servers = len(self.bot.guilds)
        users = len(self.bot.users)
        channels = sum([len(guild.channels) for guild in self.bot.guilds])
        cpu = psutil.cpu_percent()
        ram = naturalsize(psutil.Process(getpid()).memory_info().rss)
        total_ram = naturalsize(psutil.virtual_memory().total)
        pyver = python_version()
        buttons = disnake.ui.View()
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        if lang_server == 'ru':
            website = "Сайт"
            support = "Сервер поддержки"
            embed = disnake.Embed(
                title=f"Статистика бота",
                description=f"**Разработчики:** `malix.dev`, `deathofalori`, `towux`\n"
                        "\n**Основная информация:**\n"
                        f" `💬` Серверов: **{servers}**\n"
                        f"`👥` Пользователи: **{users}**\n"
                        f"`🧾` Каналы: **{channels}**\n\n"
                        "**Хостинг:**\n"
                        f"`🔥` Нагрузка: **{cpu}%**\n"
                        f"`📋` ОЗУ: **{ram} / {total_ram}**\n"
                        f"`📶` Задержка: **{round(self.bot.latency * 1000)}ms**\n\n"
                        "**О боте:** \n"
                        f"`💿` Версия бота: **{settings['botVersion']}**\n"
                        f"`💿` Версия python: `{pyver}`\n"
                        f"`📚` Библиотека: **Disnake {disnake.__version__}**\n\n"
                        "**Другое:** \n"
                        "`🔌` Платформа: **linux**\n"
                        f"`⚡` Запущено <t:{settings['uptime']}:R>", 
                color=0x2b2d31)
            embed.set_footer(text=f"Tasfers © Copyright 2022  -  {datetime.today().year}  |  Все права защищены")
        if lang_server == 'en':
            website = "Website"
            support = "Support server"
            embed = disnake.Embed(
                title=f"Bot statistics",
                description=f"**Developers:** `malix.dev`, `deathofalori`, `towux`\n"
                        "\n**Basic information:**\n"
                        f" `💬` Servers: **{servers}**\n"
                        f"`👥` Users: **{users}**\n"
                        f"`🧾` Channels: **{channels}**\n\n"
                        "**Hosting:**\n"
                        f"`🔥` Load CPU: **{cpu}%**\n"
                        f"`📋` RAM: **{ram} / {total_ram}**\n"
                        f"`📶` Ping: **{round(self.bot.latency * 1000)}ms**\n\n"
                        "**About the bot:** \n"
                        f"`💿` Bot version: **{settings['botVersion']}**\n"
                        f"`💿` python version: `{pyver}`\n"
                        f"`📚` Library: **Disnake {disnake.__version__}**\n\n"
                        "**Other:** \n"
                        "`🔌` Platform: **linux**\n"
                        f"`⚡` Launched <t:{settings['uptime']}:R>", color=0x2b2d31)
            embed.set_footer(text=f"Tasfers © Copyright 2022  -  {datetime.today().year}  |  All rights reserved")
        if lang_server == 'uk':
            website = "Сайт"
            support = "Сервер підтримки"
            embed = disnake.Embed(
                title=f"Статистика",
                description=f"**Розробники:** `malix.dev`, `deathofalori`, `towux`\n"
                        "\n**Основна інформація:**\n"
                        f" `💬` Серверів: **{servers}**\n"
                        f"`👥` Користувачі: **{users}**\n"
                        f"`🧾` Канали: **{channels}**\n\n"
                        "**Хостинг:**\n"
                        f"`🔥` Навантаження: **{cpu}%**\n"
                        f"`📋` ОЗУ: **{ram} / {total_ram}**\n"
                        f"`📶` Затримка: **{round(self.bot.latency * 1000)}ms**\n\n"
                        "**Бот:** \n"
                        f"`💿` Версія бота: **{settings['botVersion']}**\n"
                        f"`💿` Версія python: `{pyver}`\n"
                        f"`📚` Бібліотека: **Disnake {disnake.__version__}**\n\n"
                        "**інше:** \n"
                        "`🔌` Платформа: **linux**\n"
                        f"`⚡` Запущено <t:{settings['uptime']}:R>", color=0x2b2d31)
            embed.set_footer(text=f"Tasfers © Copyright 2022  -  {datetime.today().year}  |  Всі права захищені")

        buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.link, label="SD.C", url="https://bots.server-discord.com/1006946815050006539"))
        buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.link, label="Boticord", url="https://boticord.top/bot/1006946815050006539"))
        buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.link, label=website, url="https://lumix.tasfers.com"))
        buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.link, label=support, url="https://discord.gg/SpTBwz4xsa"))
        embed.set_thumbnail(url='https://media.discordapp.net/attachments/1025371600922611742/1174431100479750175/imgonline-com-ua-Shape-lg8uJpecCNjzKokp.png?ex=65679132&is=65551c32&hm=8e229723eb6d89e7a3bad679ea29a1f3d49e87ec0c3a602c728e5230959af55a&=&width=422&height=422')
        await inter.edit_original_message(embed=embed, view=buttons)


def setup(bot):
    bot.add_cog(Information(bot))
