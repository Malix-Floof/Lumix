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

import time
import disnake

from random import randint, choice
from disnake.ext import commands
from db import SQLITE


db = SQLITE("database.db")

class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False

    @commands.slash_command(
    	description=f"📌 Информация | Добавить информацию о себе",
        dm_permission=False
    )
    async def bio(self, inter, bio: str = commands.Param(name="био", description="Не указывайте персональные данные! Отображается в вашем профиле /user")):
        await inter.response.defer()
        lang = db.get(f"lang_{inter.guild.id}") or "ru"
        db.set(f"bio_{inter.author.id}", f"{bio}")
        message = {
            'ru': 'Информация была добавлена в ваш профиль',
            'en': 'Information has been added to your profile',
            'uk': 'Інформація була додана у ваш профіль'
        }[lang]
        await inter.send(message, ephemeral=True)
    
    @commands.slash_command(
        description=f"📌 Информация | Показывает информацию об участнике",
        dm_permission=False
    )
    async def user(self, inter, 
                   target: disnake.Member = commands.Param(
                       None, name="участник", 
                       description="Укажите участника"
                   )):
        await inter.response.defer()
        member = target or inter.user
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        rep = db.get(f"repytation_{member.id}") or 0
        bio = db.get(f"bio_{member.id}")
        bio = f"\n\n{bio}\n\n" if bio is not None else "Используйте команду **`/bio`**, чтобы\n добавить информацию о себе"
        if int(rep) < 0:
            rept = f"(- {rep})"
        elif int(rep) == 0:
            rept = ""
        else:
            rept = f"(+ {rep})"
        user = await self.bot.fetch_user(member.id)
        embed = disnake.Embed(description=f"{bio}", color=member.top_role.color.value)
        activities = []
        for activity in member.activities:
            if isinstance(activity, disnake.Spotify):
                if lang_server == 'ru':
                    activities.append(
                        "<:Spotify:1069625439531847771> **Spotify:**\n"
                        f"> Трек: **[{activity.title}]({activity.track_url})**\n"
                        f"> Автор: **{activity.artist}**\n"
                        f"> Длительность: **{str(activity.duration)[:7]}**"
                    )
                if lang_server == 'en':
                    activities.append(
                        "<:Spotify:1069625439531847771> **Spotify:**\n"
                        f"> Track: **[{activity.title}]({activity.track_url})**\n"
                        f"> Author: **{activity.artist}**\n"
                        f"> Duration: **{str(activity.duration)[:7]}**"
                    )
                if lang_server == 'uk':
                    activities.append(
                        "<:Spotify:1069625439531847771> **Spotify:**\n"
                        f"> Трек: **[{activity.title}]({activity.track_url})**\n"
                        f"> Автор: **{activity.artist}**\n"
                        f"> Тривалість: **{str(activity.duration)[:7]}**"
                    )
        if lang_server == 'ru':
            embed.set_author(name=f"Информация о {member.name} {rept}", icon_url=member.display_avatar)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name='Аккаунт создан:', value=f'{disnake.utils.format_dt(member.created_at, "D")}\n ({disnake.utils.format_dt(member.created_at, "R")})', inline=True)
            embed.add_field(name='Зашёл на сервер:', value=f'{disnake.utils.format_dt(member.joined_at, "D")}\n ({disnake.utils.format_dt(member.joined_at, "R")})', inline=True)
            if activities:
                embed.add_field(name=f'Активности:', value='\n'.join(activities), inline=False)
            embed.set_image(url=user.banner)
        if lang_server == 'en':
            embed.set_author(name=f"Information about {member.name} {rept}", icon_url=member.display_avatar)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name='Account created:', value=f'{disnake.utils.format_dt(member.created_at, "D")}\n ({disnake.utils.format_dt(member.created_at, "R")})', inline=True)
            embed.add_field(name='Went to the server:', value=f'{disnake.utils.format_dt(member.joined_at, "D")}\n ({disnake.utils.format_dt(member.joined_at, "R")})', inline=True)
            if activities:
                embed.add_field(name=f'Activities:', value='\n'.join(activities), inline=True)
            embed.set_image(url=user.banner)
        if lang_server == 'uk':
            embed.set_author(name=f"Інформація про {member.name} {rept}", icon_url=member.display_avatar)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name='Обліковий запис створено:', value=f'{disnake.utils.format_dt(member.created_at, "D")}\n ({disnake.utils.format_dt(member.created_at, "R")})', inline=True)
            embed.add_field(name='Зайшов на сервер:', value=f'{disnake.utils.format_dt(member.joined_at, "D")}\n ({disnake.utils.format_dt(member.joined_at, "R")})', inline=True)
            if activities:
                embed.add_field(name=f'Активності:', value='\n'.join(activities), inline=True)
            embed.set_image(url=user.banner)
        embed.set_footer(text=f"ID: {member.id}")
        await inter.send(embed=embed)
    
    @user.error
    async def on_user_error(self, inter, error):
        lang = db.get(f"lang_{inter.guild.id}") or "ru"
        if isinstance(error, commands.BadArgument):
            message = {
                'ru': 'Пользователь не найден',
                'en': 'User is not found',
                'uk': 'Користувач не знайдений'
            }[lang]
            return await inter.send(message, ephemeral=True)

    @commands.slash_command(
        description="🔧 Утилиты | Рандомное число",
        dm_permission=False
    )
    async def random(self, inter, start: int = commands.Param(name="от", description="Введите число"), end: int = commands.Param(name="до", description="Введите число")):
        lang = db.get(f"lang_{inter.guild.id}") or "ru"
        number = randint(min(start, end), max(start, end))
        message = {
            "ru": f"Ваше число: {number}",
            "en": f"Your number: {number}",
            "uk": f"Ваше число: {number}"
        }[lang]
        await inter.send(message)

    @commands.slash_command(
        description="😀 Развлечения | Добавить репутацию пользователю",
        dm_permission=False
    )
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def reputation(self, inter, member: disnake.Member = commands.Param(name="user", description="Участник"),
                         reputi: str = commands.Param(name="действие", description="Выберите действие",
                                                      choices=['Нравится', 'Не нравится'])):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        if member.bot:
            return await inter.send({
                'ru': "Вы не можете оценить бота!",
                'en': "You can't rate a bot!",
                'uk': "Ви не можете оцінити робота!"
            }[lang_server])
        if member.id == inter.author.id:
            return await inter.send({
                'ru': "Вы не можете оценить себя!",
                'en': "You can't rate yourself!",
                'uk': "Ви не можете оцінити себе!"
            }[lang_server])
        if reputi == 'Нравится':
            db.add(f"repytation_{member.id}", randint(1, 5))
            await inter.send({
                'ru': f"`💖` {inter.author.name} оценил пользователя {member.name}",
                'en': f"`💖` {inter.author.name} rated by {member.name} user",
                'uk': f"`💖` {inter.author.name} оцінив користувача {member.name}"
            }[lang_server])
        elif reputi == 'Не нравится':
            db.add(f"repytation_{member.id}", -3)
            await inter.send({
                'ru': f"`💔` {inter.author.name} понизил репутацию пользователя {member.name}",
                'en': f"`💔` {inter.author.name} lowered the reputation of user {member.name}",
                'uk': f"`💔` {inter.author.name} знизив репутацію користувача {member.name}"
            }[lang_server])

    @reputation.error
    async def on_rep_error(self, inter, error):
        if isinstance(error, commands.CommandOnCooldown):
            lang = db.get(f"lang_{inter.guild.id}") or "ru"
            timestamp = int(time.time()) + int(error.retry_after)
            message = {
                'ru': f'Вы уже оценили пользователя, вы сможете сделать это снова <t:{timestamp}:R>!',
                'en': f'Ви вже оцінили користувача, ви зможете зробити це знову <t:{timestamp}:R>!',
                'uk': f'You have already rated a user, you can do it again <t:{timestamp}:R>!'
            }[lang]
            embed = disnake.Embed(description=message, color=0x2b2d31)
            embed.set_author(name=inter.author.name, icon_url=inter.author.display_avatar)
            await inter.send(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="8ball", 
        description="😀 Развлечения | Спросить магичиский шар",
        dm_permission=False
    )
    async def ball(self, inter, text: str = commands.Param(name="вопрос", description="Задайте свой вопрос")):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        if lang_server == 'ru':
            embed = disnake.Embed(title="✨ Магический шар", color=0x2b2d31)
            embed.add_field(name='Ваш вопрос:', value=f'```\n{text}\n```', inline=False)
            message = ['Нет', 'Да', 'Не думаю', 
                   'Определённо', 'Даже не думай', 
                   'Возможно', 'Не знаю', 'Невозможно', 
                   'Карты говорят да', 'Спроси позже']
        if lang_server == 'en':
            embed = disnake.Embed(title="✨ Magic ball", color=0x2b2d31)
            embed.add_field(name='Your question:', value=f'```\n{text}\n```', inline=False)
            message = ['No', 'Yes', "I don't think",
                   'Definitely', "Don't even think",
                   'Maybe', "I don't know", 'Impossible',
                   'The cards say yes', 'Ask later']
        if lang_server == 'uk':
            embed = disnake.Embed(title="✨ Магічна куля", color=0x2b2d31)
            embed.add_field(name='Ваше запитання:', value=f'```\n{text}\n```', inline=False)
            message = ['Ні', 'Так', 'Не думаю',
                   'Певно', 'Навіть не думай',
                   'Можливо', 'Не знаю', 'Неможливо',
                   'Карти говорять так', 'Запитай пізніше']
        if lang_server == 'ru':
            embed.add_field(name='Мой ответ:', value=f'```\n{choice(message)}\n```', inline=False)
        if lang_server == 'en':
            embed.add_field(name='My answer:', value=f'```\n{choice(message)}\n```', inline=False)
        if lang_server == 'uk':
            embed.add_field(name='Моя відповідь:', value=f'```\n{choice(message)}\n```', inline=False)
        await inter.send(embed=embed)

    langs = ['Русский', 'English', 'Український']

    @commands.slash_command(description="🔧 Утилиты | Настроить язык")
    @commands.has_permissions(manage_guild=True)
    async def language(self, inter, lang: str = commands.Param(description="Смена языка", choices=langs)):
        if lang == 'Русский':
            language = db.set(f"lang_{inter.guild.id}", f"ru")
            lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
            embed = disnake.Embed(title="Язык был изменён!", description=f'Язык изменён на "Русский" (`{lang_server}`)', color=0x2b2d31)
        if lang == 'English':
            language = db.set(f"lang_{inter.guild.id}", f"en")
            lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
            embed = disnake.Embed(title="The language has been changed!", description=f'Language changed to "English" (`{lang_server}`)', color=0x2b2d31)
            embed.set_footer(text="Translation may contain errors")
        if lang == 'Український':
            language = db.set(f"lang_{inter.guild.id}", f"uk")
            lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
            embed = disnake.Embed(title="Мова була змінена!", description=f'Мова змінена на "Українську" (`{lang_server}`)', color=0x2b2d31)
            embed.set_footer(text="Переклад може містити помилки")
        await inter.send(embed=embed)

    @language.error
    async def language_error(self, inter, error):
        if isinstance(error, commands.MissingPermissions):
            lang = db.get(f"lang_{inter.guild.id}") or "ru"
            message = {
                'ru': 'У вас должно быть право на управление сервером что бы установить язык',
                'en': 'You must have the right to manage the server in order to set the language',
                'uk': 'У вас має бути право на керування сервером щоб встановити мову'
            }[lang]
            await inter.send(message, ephemeral=True)

def setup(bot):
    bot.add_cog(Main(bot))
