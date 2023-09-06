import disnake
from disnake.ext import commands
from config import settings
import time
import psutil
from platform import python_version
from humanize import naturalsize
from datetime import datetime
from os import getpid
import lumix.print
from db import SQLITE

db = SQLITE("database.db")
start_time = time.time()


class Information(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"bot.py is ready")

    @commands.slash_command(description=f"📌 Информация | Показывает статистику бота")
    async def bot(self, inter):
        await inter.response.defer()
        servers = len(self.bot.guilds)
        users = len(set(self.bot.get_all_members()))
        channels = sum([len(guild.channels) for guild in self.bot.guilds])

        cpu = psutil.cpu_percent()
        ram = naturalsize(psutil.Process(getpid()).memory_info().rss)
        mram = naturalsize(self.bot.node.stats.memory_used)
        pyver = python_version()

        elapsed_time = time.time() - start_time
        days = int(elapsed_time // 86400)
        hours = int((elapsed_time - days * 86400) // 3600)
        minutes = int((elapsed_time - days * 86400 - hours * 3600) // 60)
        buttons = disnake.ui.View()
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        if lang_server == 'ru':
            website = "Сайт"
            support = "Сервер поддержки"
            embed = disnake.Embed(
                title=f"Статистика бота",
                description=f"**Разработчики:** `malix.dev`, `towux`,\n `kotik_nekot`, `thdev_off`, `fya.dev`\n"
                        "\n**Основная информация:**\n"
                        f" `💬` Серверов: **{servers}**\n"
                        f"`👥` Пользователи: **{users}**\n"
                        f"`🧾` Каналы: **{channels}**\n\n"
                        "**Хостинг:**\n"
                        f"`🔥` Нагрузка: **{cpu}%**\n"
                        f"`📋` ОЗУ: **{ram} / 2 GB**\n"
                        f"`📶` Задержка: **{round(self.bot.latency * 1000)}ms**\n\n"
                        "**Музыкальный сервер:**\n"
                        f"`🔥` Нагрузка: **{self.bot.node.stats.system_load:.2f}%**\n"
                        f"`📋` ОЗУ: **{mram} / 2 GB**\n"
                        f"`💿` Сейчас играет **{self.bot.node.stats.playing_players}** плеер(-ов)\n\n"
                        "**О боте:** \n"
                        f"`💿` Версия бота: **v3.6**\n"
                        f"`💿` Версия python: `{pyver}`\n"
                        "`📚` Библиотека: **Disnake**\n"
                        f"`📚` Версия Disnake: **{disnake.__version__}**\n\n"
                        "**Другое:** \n"
                        "`🔌` Платформа: **linux**\n"
                        f"`⚡` Время работы бота: `{days} дней, {hours} часов, {minutes} минут`", color=0x2b2d31)
            embed.set_footer(text=f"Tasfers © Copyright 2022 - {datetime.today().year} | Все права защищены")
        if lang_server == 'en':
            website = "Website"
            support = "Support server"
            embed = disnake.Embed(
                title=f"Bot statistics",
                description=f"**Developers:** `malix.dev`, `towux`,\n `kotik_nekot`, `thdev_off`, `fya.dev`\n"
                        "\n**Basic information:**\n"
                        f" `💬` Servers: **{servers}**\n"
                        f"`👥` Users: **{users}**\n"
                        f"`🧾` Channels: **{channels}**\n\n"
                        "**Hosting:**\n"
                        f"`🔥` Load CPU: **{cpu}%**\n"
                        f"`📋` RAM: **{ram} / 2 GB**\n"
                        f"`📶` Ping: **{round(self.bot.latency * 1000)}ms**\n\n"
                        "**Lavalink server:**\n"
                        f"`🔥` Load server: **{self.bot.node.stats.system_load:.2f}%**\n"
                        f"`📋` RAM: **{mram} / 2 GB**\n"
                        f"`💿` Now playing **{self.bot.node.stats.playing_players}** player(s)\n\n"
                        "**About the bot:** \n"
                        f"`💿` Bot version: **v3.6**\n"
                        f"`💿` python version: `{pyver}`\n"
                        "`📚` Library: **Disnake**\n"
                        f"`📚` Disnake version: **{disnake.__version__}**\n\n"
                        "**Other:** \n"
                        "`🔌` Platform: **linux**\n"
                        f"`⚡` Uptime: `{days} days, {hours} hours, {minutes} minutes`", color=0x2b2d31)
            embed.set_footer(text=f"Tasfers © Copyright 2022 - {datetime.today().year} | All rights reserved")
        if lang_server == 'uk':
            website = "Сайт"
            support = "Сервер підтримки"
            embed = disnake.Embed(
                title=f"Статистика",
                description=f"**Розробники:** `malix.dev`, `towux`,\n `kotik_nekot`, `thdev_off`, `fya.dev`\n"
                        "\n**Основна інформація:**\n"
                        f" `💬` Серверів: **{servers}**\n"
                        f"`👥` Користувачі: **{users}**\n"
                        f"`🧾` Канали: **{channels}**\n\n"
                        "**Хостинг:**\n"
                        f"`🔥` Навантаження: **{cpu}%**\n"
                        f"`📋` ОЗУ: **{ram} / 2 GB**\n"
                        f"`📶` Затримка: **{round(self.bot.latency * 1000)}ms**\n\n"
                        "**Музичний сервер:**\n"
                        f"`🔥` Навантаження: **{self.bot.node.stats.system_load:.2f}%**\n"
                        f"`📋` ОЗУ: **{mram} / 2 GB**\n"
                        f"`💿` Зараз грає **{self.bot.node.stats.playing_players}** плеєр(-ів)\n\n"
                        "**Бот:** \n"
                        f"`💿` Версія бота: **v3.6**\n"
                        f"`💿` Версія python: `{pyver}`\n"
                        "`📚` Бібліотека: **Disnake**\n"
                        f"`📚` Версія Disnake: **{disnake.__version__}**\n\n"
                        "**інше:** \n"
                        "`🔌` Платформа: **linux**\n"
                        f"`⚡` Час роботи бота: `{days} днів, {hours} годин, {minutes} хвилин`", color=0x2b2d31)
            embed.set_footer(text=f"Tasfers © Copyright 2022 - {datetime.today().year} | Всі права захищені")

        buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.link, label="SD.C", url="https://bots.server-discord.com/1006946815050006539"))
        buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.link, label="Boticord", url="https://boticord.top/bot/1006946815050006539"))
        buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.link, label=website, url="https://lumix.tasfers.com"))
        buttons.add_item(disnake.ui.Button(style=disnake.ButtonStyle.link, label=support, url="https://discord.gg/SpTBwz4xsa"))
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1025371600922611742/1061723917678551050/imgonline-com-ua-Shape-ytA3LtnDI8wQ9nZ.png')
        await inter.edit_original_message(embed=embed, view=buttons)


def setup(bot):
    bot.add_cog(Information(bot))
