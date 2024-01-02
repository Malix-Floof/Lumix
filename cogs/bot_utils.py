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
from gtts import gTTS
from db import SQLITE

db = SQLITE("database.db")


class CogUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False

    @commands.Cog.listener()
    async def on_ready(self):
        print("utils.py is ready")
        await db.initialize()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        autorole = db.get(f"autorole_{member.guild.id}")
        if autorole is None:
            return
        role = disnake.utils.get(member.guild.roles, id=int(autorole))
        await member.add_roles(role)

    @commands.slash_command(description="Установить автороли на сервер!")
    @commands.has_permissions(administrator=True)
    async def autorole(self, inter, role: disnake.Role):
        if role.position == 0:
            return await inter.send('Давайте оставим `@everyone` для объявлений и общих уведомлений, а автороли сделаем более уникальными, ок?', ephemeral=True)
            
        if role.is_premium_subscriber():
            return await inter.send('Эх, роль бустера слишком "взрывная" для авторолей, она настролько крутая, что я не могу её выдать автоматически!', ephemeral=True)

        if role.is_integration():
            return await inter.send('Ого, роль интеграции в автороли? Ну-ну, следующий шаг - автоматические сообщения от тостера! Лучше оставим интеграции на их месте и не путаем роли с пирожками!', ephemeral=True)

        if role.is_bot_managed():
            return await inter.send('Роль приложения? Ну, она такая особенная, что даже автороли не могут ее понять! Ловите ошибку 404: Роль приложения не может быть установлена в качестве роли для авторолей', ephemeral=True)

        await db.set(f"autorole_{inter.guild.id}", str(role.id))
        embed = disnake.Embed(description=f"**Когда кто-то присоединяется к серверу, роль <@&{role.id}> будет автоматически выдана пользователю**", color=0x2b2d31)
        await inter.send(embed=embed)

    @autorole.error
    async def autorole_error(self, inter, error):
        await db.get(f"lang_{inter.guild.id}") or "ru"
        if isinstance(error, commands.MissingPermissions):
                await inter.send("У вас должно быть право администратора что бы установить автоматическую выдачу ролей", ephemeral=True)


    @commands.slash_command(description="🔧 Утилиты | Показать баннер участника")
    async def banner(self, inter, member: disnake.Member = commands.Param(None, name="участник", description="Укажите участника")):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        if member is None:
            member = await self.bot.fetch_user(inter.author.id)
        else:
            member = await self.bot.fetch_user(member.id)

        if member.banner is None:
            if lang_server == 'ru':
                await inter.send("У пользователя не установлен баннер", ephemeral=True)
            if lang_server == 'en':
                await inter.send("The user does not have a banner", ephemeral=True)
            if lang_server == 'uk':
                await inter.send("У користувача не встановлено банер", ephemeral=True)
        else:
            if lang_server == 'ru':
                embed = disnake.Embed(title=f"Баннер — {member}", description=f"[Скачать]({member.banner})", color=0x2b2d31)
            if lang_server == 'en':
                embed = disnake.Embed(title=f"Banner — {member}", description=f"[Download]({member.banner})", color=0x2b2d31)
            if lang_server == 'uk':
                embed = disnake.Embed(title=f"Банер — {member}", description=f"[Завантажити]({member.banner})", color=0x2b2d31)
            embed.set_image(url=member.banner)
            await inter.send(embed=embed)

    langs = ['Английский', 'Арабский', 'Белорусский', 'Русский', 'Украинский']

    @commands.slash_command(description="🔧 Утилиты | Создать озвучку")
    async def gtts(self, inter, lang: str = commands.Param(name="язык", description="Выберите язык для озвучивания", choices=langs), text: str = commands.Param(name="текст", description="Какой текст озвучить?")):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        lang_map = {
            'Английский': 'en',
            'Арабский': 'ar',
            'Белорусский': 'be',
            'Русский': 'ru',
            'Украинский': 'uk'
        }

        tts = gTTS(text=text, lang=lang_map[lang])
        tts.save(f"./src/audio/gtts/{lang_map[lang]}-voice.mp3")
        file = disnake.File(f"./src/audio/gtts/{lang_map[lang]}-voice.mp3")
        message = {
            'ru': 'Результат:',
            'en': 'Result:',
            'uk': 'Результат:'    
        }[lang_server]
        await inter.send(message, file=file)

    @gtts.error
    async def gtts_error(self, inter):
        lang = db.get(f"lang_{inter.guild.id}") or "ru"
        message = {
            'ru': 'Простите, данный язык сейчас не доступен!',
            'en': 'Sorry, this language is currently not available!',
            'uk': 'Вибачте, ця мова зараз не доступна!'    
        }[lang]
        embed = disnake.Embed(description=message, color=0x2b2d31)
        embed.set_author(name=inter.author.name, icon_url=inter.user.display_avatar.url)
        await inter.send(embed=embed)


    @commands.slash_command(description="🔧 Утилиты | Показывает аватарку пользователя")
    async def avatar(self, inter, user: disnake.Member = commands.Param(None, name="пользователь", description="Выберите пользователя")):
        lang = db.get(f"lang_{inter.guild.id}") or "ru"
        if user is None:
            user = inter.user
            formats = [
                f"PNG({user.display_avatar.replace(format='png', size=1024).url}) | ",
                f"JPG({user.display_avatar.replace(format='jpg', size=1024).url})",
                f" | WebP({user.display_avatar.replace(format='WebP', size=1024).url})",
                f" | GIF({user.display_avatar.replace(format='gif', size=1024).url})" if user.display_avatar.is_animated() else ""
            ]
            message = {
                'ru': 'Твоя аватарка',
                'en': 'You avatar',
                'uk': 'Твоя аватарка'    
            }[lang]
            embed = disnake.Embed(title=message, description=' '.join(formats), color=0x2b2d31)
            embed.set_image(url=inter.user.display_avatar.url)
            await inter.send(embed=embed)
        else:
            formats = [
                f"[PNG]({user.display_avatar.replace(format='png', size=1024).url}) | ",
                f"[JPG]({user.display_avatar.replace(format='jpg', size=1024).url})",
                f" | [WebP]({user.display_avatar.replace(format='webp', size=1024).url})",
                f" | [GIF]({user.display_avatar.replace(format='gif', size=1024).url})" if user.display_avatar.is_animated() else ""
            ]
            if lang == 'ru':
                embed = disnake.Embed(title=f"Аватарка {'бота' if user.bot else 'пользователя'} {user.name}", description=' '.join(formats), color=0x2b2d31)
            if lang == 'en':
                embed = disnake.Embed(title=f"{'Bot' if user.bot else 'User'} avatar {user.name}", description=' '.join(formats), color=0x2b2d31)
            if lang == 'uk':
                embed = disnake.Embed(title=f"Аватарка {'бота' if user.bot else 'користувача'} {user.name}", description=' '.join(formats), color=0x2b2d31)
            embed.set_image(url=user.display_avatar.url)
            await inter.send(embed=embed)


def setup(bot):
    bot.add_cog(CogUtils(bot))
