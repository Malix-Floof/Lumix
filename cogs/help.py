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
from db import SQLITE

db = SQLITE("database.db")

class CogHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member): # FIXME: later... 🙄
        autorole = db.get(f"autorole_{member.guild.id}")
        if autorole is None:
            return

        role = disnake.utils.get(member.guild.roles, id=int(autorole))
        await member.add_roles(role)


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        embed = disnake.Embed(
            description=f"🇷🇺 **Спасибо за приглашение!** Мы рады, что вы выбрали нашего бота и добавили его на ваш замечательный сервер - **{guild.name}**! Чтобы сменить язык используйте `/language`. Также вы можете посетить наш [**сайт**](https://lumix.tasfers.com) и [**сервер поддержки**](https://discord.gg/SpTBwz4xsa).\n\n🇺🇸 **Thanks for the invitation!** We are glad that you have chosen our bot and added it to your wonderful server - **{guild.name}**! To change the language use `/language`. You can also visit our [**website**](https://lumix.tasfers.com) and [**support server**](https://discord.gg/SpTBwz4xsa).\n\n🇺🇦 **Дякую за запрошення!** Ми раді, що ви вибрали нашого бота і додали його на ваш чудовий сервер - **{guild.name}**! Щоб змінити мову, використовуйте `/language`. Також ви можете відвідати наш [**сайт**](https://lumix.tasfers.com) та [**сервер підтримки**](https://discord.gg/SpTBwz4xsa).", 
            color=0x2b2d31
        )
        embed.set_footer(text=f"{guild.name}  •  {guild.id}", icon_url=guild.icon)
        try:
            await guild.owner.send(embed=embed)
        except Exception:
            ...

    @commands.slash_command(description="📌 Информация | Помощь по боту")
    async def help(self, inter):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        if lang_server == 'ru':
            embed = disnake.Embed(
                title="Доступные команды **[25]**:",
                description="> **`📚` Информация:**\n"
                "`/bot` - Информация о боте\n"
                "`/server` - Информация о сервере\n"
                "`/user` - Информация о участнике\n\n"
                "> **`😀` Развлечения:**\n"
                "`/animal` - Получить пикчу и факт о животных\n"
                "`/brush` - Покраснеть\n"
                "`/cry` - Заплакть\n"
                "`/dance` - Танцевать\n"
                "`/happy` - Радоваться\n"
                "`/emote` - Взаимодействия с участником\n\n"
                "> **`🔨` Модерация:**\n"
                "`/ban` - Забанить пользователя\n"
                "`/unban` - Разбанить пользователя\n"
                "`/mute` - Замутить пользователя\n"
                "`/unmute` - Размутить пользователя\n"
                "`/clear` - Отчистить N сообщений в чате\n"
                "`/slowmode` - Установить задержку между сообщениями в чате (0 что бы убрать)\n\n"
                "> **`🔧` Утилиты:**\n"
                "`/avatar` - Получить аватар пользователя\n"
                "`/banner` - Получить баннер пользователя\n"
                "`/setlogchannel` - Установить канал с логами\n"
                "`/autorole` - Настроить автороли\n"
                "`/filter` - Наложить фильтр на аватарку пользователя\n"
                "`/gtts` - Создать озвучку\n"
                "`/random` - Рандомное число\n\n"
                "> **`🎶` Музыка:**\n"
                "`/play` - Включить трек в голосовом канале\n"
                "`/stop` - Отчистить очередь сервера\n"
                "`/volume` - Изменить громкость трека",
                color=0x2b2d31
            )
        if lang_server == 'en':
            embed = disnake.Embed(
                title="Available commands **[25]**:",
                description="> **`📚` Information:**\n"
                "`/bot` - Bot Information\n"
                "`/server` - Server Information\n"
                "`/user` - User Information\n\n"
                "> **`😀` Fun:**\n"
                "`/animal` - Get picture and fact about animals\n"
                "`/brush` - Blush\n"
                "`/cry` - Cry\n"
                "`/dance` - Dance\n"
                "`/happy` - Happy\n"
                "`/emote` - Member Interactions\n\n"
                "> **`🔨` Moderation:**\n"
                "`/ban` - Ban user\n"
                "`/unban` - Unban user\n"
                "`/mute` - Mute user\n"
                "`/unmute` - Unmute user\n"
                "`/clear` - Clear N messages in chat\n"
                "`/slowmode` - Set a delay between chat messages (0 to remove)\n\n"
                "> **`🔧` Utilities:**\n"
                "`/avatar` - Get user avatar\n"
                "`/banner` - Get user banner\n"
                "`/setlogchannel` - Set log channel\n"
                "`/autorole` - Configure autoroles\n"
                "`/filter` - Apply a filter to the user's profile picture\n"
                "`/gtts` - Create Voiceover\n"
                "`/random` - Random number\n\n"
                "> **`🎶` Music:**\n"
                "`/play` - Enable track in voice channel\n"
                "`/stop` - Clear the server queue\n"
                "`/volume` - Change track volume",
                color=0x2b2d31
            )
        if lang_server == 'uk':
            embed = disnake.Embed(
                title="Доступні команди **[25]**:",
                description="> **`📚` Інформація:**\n"
                "`/bot` - Інформація про бота\n"
                "`/server` - Інформація про сервер\n"
                "`/user` - Інформація про користувача\n\n"
                "> **`😀` Розваги:**\n"
                "`/animal` - Отримати пікчу та факт про тварин\n"
                "`/brush` - Рум'яна\n"
                "`/cry` - Плакати\n"
                "`/dance` - Танець\n"
                "`/happy` - Щаслива\n"
                "`/emote` - Взаємодія з учасниками\n\n"
                "> **`🔨` Модерація:**\n"
                "`/ban` - Забанити користувача\n"
                "`/unban` - Розблокувати користувача\n"
                "`/mute` - Вимкнути звук користувача\n"
                "`/unmute` - Увімкнути звук користувача\n"
                "`/clear` - Очистити N повідомлень у чаті\n"
                "`/slowmode` - Установити затримку між повідомленнями чату (0, щоб видалити)\n\n"
                "> **`🔧` Комунальні послуги:**\n"
                "`/avatar` - Отримати аватар користувача\n"
                "`/banner` - Отримати банер користувача\n"
                "`/setlogchannel` - Встановити канал з логами\n"
                "`/autorole` - Налаштувати авторолі\n"
                "`/filter` - Застосуйте фільтр до зображення профілю користувача\n"
                "`/gtts` - Створення озвучення\n"
                "`/random` - Рандомне число\n\n"
                "> **`🎶` Музика:**\n"
                "`/play` - Увімкнути трек у голосовому каналі\n"
                "`/stop` - Очистіть чергу сервера\n"
                "`/volume` - Змінити гучність треку",
                color=0x2b2d31
            )
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1025371600922611742/1061723917678551050/imgonline-com-ua-Shape-ytA3LtnDI8wQ9nZ.png')
        await inter.send(embed=embed)


    @commands.slash_command(description=f"📌 Информация | Показывает информацию о сервере")
    async def server(self, inter):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        guild = inter.guild
        bots = 0
        humans = 0
        online = 0
        offline = 0
        idle = 0
        dnd = 0
        for member in inter.guild.members:
            if member.bot:
                bots += 1
            else:
                humans += 1
                status = member.status
                if status == disnake.Status.online:
                    online += 1
                elif status == disnake.Status.offline:
                    offline += 1
                elif status == disnake.Status.idle:
                    idle += 1
                elif status == disnake.Status.dnd:
                    dnd += 1
        sdate = disnake.utils.format_dt(guild.created_at, "R")
        ddate = disnake.utils.format_dt(guild.created_at, "D")
        s = f"{guild.verification_level}"
        text = {
            'ru': (("none", "Отсуствует"), ("low", "Низкий"), ("medium", "Средний"), ("highest", "Самый высокий"), ("high", "Высокий")),
            'uk': (("none", "Відсутнiй"), ("low", "Низький"), ("medium", "Середній"), ("highest", "Найвищий"), ("high", "Високий")),
            'en': (("none", "None"), ("low", "Low"), ("medium", "Medium"), ("highest", "Highest"), ("high", "High"))
        }[lang_server]

        for r in text:
            s = s.replace(*r)
        
        servertext = {
            'ru': 'Отсутствует',
            'en': 'Absent',
            'uk': 'Відсутнiй'
        }[lang_server]
        servertext = guild.description or servertext
        if lang_server == 'ru':
            embed = disnake.Embed(title=f"Информация о сервере {guild.name}", description=f"Владелец: {guild.owner.mention} (`{guild.owner.name}`)\nДата создания: **{ddate} ({sdate})**\nУровень верификации: {s}\nОписание: {servertext}\n", color=0x2b2d31)
            embed.add_field(name="> Участники:", value=f"Всего: **{humans + bots}**\nУчастники: **{humans}**\nБотов **{bots}**", inline=True)
            embed.add_field(name="> Статусы:", value=f"В сети: **{online}**\nНеактивен: **{idle}**\nНе беспокоить: **{dnd}**\nНе в сети: **{offline}**", inline=True)
            embed.add_field(name="> Каналы:", value=f"Текстовых: **{len(guild.text_channels)}**\nГолосовых: **{len(guild.voice_channels)}**\nТрибун: **{len(guild.stage_channels)}**\nФорумов: **{len(guild.forum_channels)}**", inline=True)
            embed.set_image(url=guild.banner)
            embed.set_thumbnail(url=guild.icon)
            embed.set_footer(text=f"ID: {guild.id}  -  Звено: #{guild.shard_id}")
        if lang_server == 'en':
            embed = disnake.Embed(title=f"{guild.name} server information", description=f"Owner: {guild.owner.mention} (`{guild.owner.name}`)\nDate of creation: **{ddate} ({sdate})**\nVerification level: {s}\nDescription: {servertext}\n", color=0x2b2d31)
            embed.add_field(name="> Members:", value=f"All: **{humans + bots}**\nMembers: **{humans}**\nBots **{bots}**", inline=True)
            embed.add_field(name="> Statuses:", value=f"Online: **{online}**\nInactive: **{idle}**\nDo not disturb: **{dnd}**\nOffline: **{offline}**", inline=True)
            embed.add_field(name="> Channels:", value=f"Text: **{len(guild.text_channels)}**\nVoice: **{len(guild.voice_channels)}**\nTribune: **{len(guild.stage_channels)}**\nForums: **{len(guild.forum_channels)}**", inline=True)
            embed.set_image(url=guild.banner)
            embed.set_thumbnail(url=guild.icon)
            embed.set_footer(text=f"ID: {guild.id}  -  Shard: #{guild.shard_id}")
        if lang_server == 'uk':
            embed = disnake.Embed(title=f"Інформація про сервер {guild.name}", description=f"Власник: {guild.owner.mention} (`{guild.owner.name}`)\nДата створення: **{ddate} ({sdate})**\nРівень верифікації: {s}\nОпис: {servertext}\n", color=0x2b2d31)
            embed.add_field(name="> Участники:", value=f"Усього: **{humans + bots}**\nУчастники: **{humans}**\nБотов **{bots}**", inline=True)
            embed.add_field(name="> Статуси:", value=f"В мережі: **{online}**\nНеактивний: **{idle}**\nНе турбувати: **{dnd}**\nНе в мережі: **{offline}**", inline=True)
            embed.add_field(name="> Канали:", value=f"Текстових: **{len(guild.text_channels)}**\nГолосових: **{len(guild.voice_channels)}**\nТрибун: **{len(guild.stage_channels)}**\nФорумів: **{len(guild.forum_channels)}**", inline=True)
            embed.set_image(url=guild.banner)
            embed.set_thumbnail(url=guild.icon)
            embed.set_footer(text=f"ID: {guild.id}  -  Ланка: #{guild.shard_id}")
        await inter.send(embed=embed)

def setup(bot):
    bot.add_cog(CogHelp(bot))
