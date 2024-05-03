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
import re
from random import choice, randint
from disnake.ext import commands
from datetime import *
from db import SQLITE

db = SQLITE("database.db")


class Moder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.slash_command(description="🛡️ Удаляет сообщения")
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def clear(self, inter: disnake.ApplicationCommandInteraction, amount: commands.Range[int, 1, 100] = commands.Param(
                name="количество", description="Лимит для удаления сообщений: 100")):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        await inter.response.defer(ephemeral=True)
        try:
            await inter.channel.purge(limit=amount)
        except disnake.Forbidden:
            return await inter.send("У бота нет прав для управления сообщениями", ephemeral=True)
        message = {
            'ru': f'Вы очистили `{amount}` сообщений',
            'en': f'You cleared `{amount}` messages',
            'uk': f'Ви очистили `{amount}` повідомлень'
        }[lang_server]
        await inter.edit_original_message(embed=disnake.Embed(description=message, color=0x2b2d31))

    @clear.error
    async def clear_error(self, inter: disnake.ApplicationCommandInteraction, error):
        lang = db.get(f"lang_{inter.guild.id}") or "ru"
        if isinstance(error, disnake.Forbidden):
            message = {
                'ru': 'У бота недостаточно прав для отчистки сообщений',
                'en': 'The bot does not have enough rights to clear messages',
                'uk': 'У бота недостатньо прав для очищення повідомлень'
            }[lang]
            return await inter.send(message, ephemeral=True)
        if isinstance(error, commands.BotMissingPermissions):
            message = {
                'ru': 'У бота недостаточно прав для отчистки сообщений',
                'en': 'The bot does not have enough rights to clear messages',
                'uk': 'У бота недостатньо прав для очищення повідомлень'
            }[lang]
            return await inter.send(message, ephemeral=True)
        if isinstance(error, commands.MissingPermissions):
            message = {
                'ru': 'У вас недостаточно прав для отчистки сообщений',
                'en': "You don't have enough rights to clear messages",
                'uk': 'У вас недостатньо прав для очищення повідомлень'
            }[lang]
            return await inter.send(message, ephemeral=True)
        
        await inter.send("Что-то пошло не так, и тип этой ошибки просто невозможно определить", ephemeral=True)

    @commands.slash_command(description="🛡️ Даёт мут пользователю")
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    async def mute(self, inter: disnake.ApplicationCommandInteraction,
                   member: disnake.Member = commands.Param(name='пользователь', description="Пользователь для мута"),
                   duration: str = commands.Param(name="время", description="1w 1d 15h 30m 30s"),
                   reason: str = commands.Param("Не указана", name="причина", description="Причина мута")
                  ) -> None:
        lang = db.get(f"lang_{inter.guild.id}") or "ru"
        durations = duration.split()
        
        joke = ["Ха-ха, ну что у нас тут! Кажется, что-то пошло не по плану... Но подожди-ка, я вижу, этот участник, владелец сервера, просто неприступен! Он как незаглушимый супергерой, готовый отразить все мои попытки! Я чувствую себя просто как бедный злодей, пытающийся поймать моего супергеройского противника! Ха-ха-ха!",
                "Ой-ой, что-то пошло не по плану! Но стоп-стоп-стоп! У меня есть ощущение, что этот участник, владелец сервера, просто неприступен! Он как незаглушимый супергерой, готовый сразиться со всеми моими попытками! Я чувствую себя просто как злодей из комиксов, пытающийся поймать этого непобедимого героя! Ха-ха-ха!",
                "О нет, все идет не так... И я понимаю, этот участник, владелец сервера, непробиваемый. Он словно супергерой, готовый отразить все мои попытки. Мои усилия напрасны...",
                "Ох, ничего не получается! Он просто непокоримый материал, словно незаглушимый супергерой, который насмехается над моими попытками! Я злюсь и бушую от раздражения! Почему он так непробиваем?!"]

        if member.id == inter.guild.owner.id:
            return await inter.send(choice(joke), ephemeral=True)

        if member.current_timeout:
            timestipo = datetime.strptime(f"{member.current_timeout}", "%Y-%m-%d %H:%M:%S.%f%z").timestamp()
            message = {
                'ru': f'Пользователь уже заглушен! Время заглушки истечёт <t:{int(timestipo)}:R>',
                'en': f'The user is already muted! Stub timeout <t:{int(timestipo)}:R>',
                'uk': f'Користувач уже заглушено! Час заглушки мине <t:{int(timestipo)}:R>'
            }[lang]
            embed = disnake.Embed(description=message, color=0x2b2d31)
            return await inter.send(embed=embed, ephemeral=True)

        if member.top_role > inter.guild.me.top_role:
            return await inter.send(f"**{inter.author.global_name}** чтобы заглушить участника, необходимо установить мою роль выше остальных ролей, так как роль участника имеет более высокий приоритет, чем моя. В противном случае я не смогу заглушить участника", ephemeral=True)
        for dur in durations:
            if not re.match(r'^\d+[wdhms]$', dur):
                message = {
                    'ru': 'Неверный формат времени.\n\ns - секунды\nm - минуты\nh - часы\nd - дни\nw - недели\n\nПример: 15m (заглушит участника на 15 минут)\nМаксимальная длительность заглушки: месяц (4w)',
                    'en': 'Invalid time format.\n\ns - seconds\nm - minutes\nh - hours\nd - days\nw - weeks\n\nExample: 15m (will mute the participant for 15 minutes)\nMaximum mute duration: month (4w)',
                    'uk': 'Неправильний формат часу.\n\ns - секунди\nm - хвилини\nh - години\nd - дні\nw - тижні\n\nПриклад: 15m (заглушить учасника на 15 хвилин)\nМаксимальна тривалість заглушки: місяць (4w)'
                }
                return await inter.send(message[lang], ephemeral=True)

        total_seconds = 0
        for dur in durations:
            val = int(dur[:-1])
            unit = dur[-1].lower()
            if unit == 's':
                total_seconds += val
            elif unit == 'm':
                total_seconds += val * 60
            elif unit == 'h':
                total_seconds += val * 60 * 60
            elif unit == 'd':
                total_seconds += val * 24 * 60 * 60
            elif unit == 'w':
                total_seconds += val * 7 * 24 * 60 * 60
                
        timestamp = ""
        try:
            await member.edit(timeout=total_seconds, reason=reason[:50])
            timestamp = int(datetime.strptime(f"{member.current_timeout}", "%Y-%m-%d %H:%M:%S.%f%z").timestamp())
        except disnake.HTTPException:
            return await inter.send("Похоже что вы пытаетесь заглушить участника на более большее время чем 1 месяц, попробуйте: 4w", ephemeral=True)
        except disnake.Forbidden:
            return await inter.send("У бота недостаточно прав для управления пользователями", ephemeral=True)
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        if lang_server == 'ru':
            embed = disnake.Embed(
                title="Блокировка в чате", 
                description=f"Истечет <t:{timestamp}:f> (<t:{timestamp}:R>)", 
                color=0x2b2d31
            )
            embed.add_field(name="Пользователь:", value=f"{member.mention}", inline=True)
            embed.add_field(name="Модератор:", value=f"{inter.author.mention}", inline=True)
            embed.add_field(name="Причина:", value=f"`{reason[:50]}`", inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)
        if lang_server == 'en':
            embed = disnake.Embed(
                title="Blocking in the chat",
                description=f"Expires <t:{timestamp}:f> (<t:{timestamp}:R>)",
                color=0x2b2d31
            )
            embed.add_field(name="User:", value=f"{member.mention}", inline=True)
            embed.add_field(name="Мoderator:", value=f"{inter.author.mention}", inline=True)
            embed.add_field(name="Reason:", value=f"`{reason[:50]}`", inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)
        if lang_server == 'uk':
            embed = disnake.Embed(
                title="Блокування в чаті",
                description=f"Визначити <t:{timestamp}:f> (<t:{timestamp}:R>)",
                color=0x2b2d31
            )
            embed.add_field(name="Користувач:", value=f"{member.mention}", inline=True)
            embed.add_field(name="Модератор:", value=f"{inter.author.mention}", inline=True)
            embed.add_field(name="Причина:", value=f"`{reason[:50]}`", inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)
            if randint(1,10) == 1:
                embed.set_image(url='https://media1.tenor.com/m/u3qFV6qjvQIAAAAd/%D1%82%D1%8B-%D0%B2-%D0%BC%D1%83%D1%82%D0%B5-muted.gif')

        await inter.send(embed=embed)

    @mute.error
    async def mute_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, disnake.Forbidden):
            return await inter.send("У вас недостаточно прав для управления пользователями", ephemeral=True)
        if isinstance(error, commands.MissingPermissions):
            return await inter.send("У вас недостаточно прав для управления пользователями", ephemeral=True)
        if isinstance(error, commands.BotMissingPermissions):
            return await inter.send("У бота недостаточно прав для управления пользователями", ephemeral=True)
        if isinstance(error, commands.BadArgument):
            return await inter.send("Пользователь не найден на сервере ¯\_(ツ)_/¯", ephemeral=True)
        
        await inter.send("Что-то пошло не так, и тип этой ошибки просто невозможно определить", ephemeral=True)

    @commands.slash_command(description="🛡️ Устанавливает медленный режим для текущего канала")
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, inter: disnake.ApplicationCommandInteraction, 
                       seconds: commands.Range[int, 0, 21000] = commands.Param(
                           name='секунды', description="Задержка между сообщениями")):
        await inter.response.defer()
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        try:
            await inter.channel.edit(slowmode_delay=seconds)
        except disnake.Forbidden:
            return await inter.send("У бота не достаточно прав для управления каналами", ephemeral=True)

        time_units = {
            'ru': {'hours': 'часов ', 'minutes': 'минут ', 'seconds': 'секунд '},
            'en': {'hours': 'hours ', 'minutes': 'minutes ', 'seconds': 'seconds '},
            'uk': {'hours': 'годин ', 'minutes': 'хвилин ', 'seconds': 'секунд '}
        }

        hours = seconds // 3600
        seconds %= 3600

        minutes = seconds // 60
        seconds %= 60

        time_formatted = ""
        if hours > 0:
            time_formatted += f"{hours} {time_units[lang_server]['hours']}"
        if minutes > 0:
            time_formatted += f"{minutes} {time_units[lang_server]['minutes']}"
        if seconds > 0:
            time_formatted += f"{seconds} {time_units[lang_server]['seconds']}"

        if seconds == 0:
            message = {
                'ru': [{
                    'title': 'Медленный режим',
                    'description': 'Медленный режим был отключён'
                }],
                'en': [{
                    'title': 'Slow mode',
                    'description': 'Slow mode has been disabled',
                }],
                'uk': [{
                    'title': 'Повільний режим',
                    'description': 'Повільний режим був вимкнений'
                }]
            }
            embed = disnake.Embed(
                title=message[lang_server][0]['title'],
                description=message[lang_server][0]['description'],
                color=0x2b2d31
            )
        else:
            message = {
                'ru': [{
                    'title': 'Медленный режим',
                    'description': f'Медленный режим установлен на `{time_formatted}`'
                }],
                'en': [{
                    'title': 'Slow mode',
                    'description': f'Slow mode set to `{time_formatted}`',
                }],
                'uk': [{
                    'title': 'Повільний режим',
                    'description': f'Повільний режим встановлено на `{time_formatted}`'
                }]
            }
            embed = disnake.Embed(
                title=message[lang_server][0]['title'],
                description=message[lang_server][0]['description'],
                color=0x2b2d31
            )
        await inter.send(embed=embed)

    @slowmode.error
    async def slowmode_error(self, inter: disnake.ApplicationCommandInteraction, error):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        if isinstance(error, disnake.Forbidden):
            message = {
                'ru': 'У бота недостаточно прав для установки задержки в чате',
                'en': 'The bot does not have enough rights to set a chat delay',
                'uk': 'У бота недостатньо прав для встановлення затримки в чаті'
            }
            await inter.send(message[lang_server], ephemeral=True)
            return
        if isinstance(error, commands.BotMissingPermissions):
            message = {
                'ru': 'У бота недостаточно прав для установки задержки в чате',
                'en': 'The bot does not have enough rights to set a chat delay',
                'uk': 'У бота недостатньо прав для встановлення затримки в чаті'
            }
            await inter.send(message[lang_server], ephemeral=True)
            return 
        if isinstance(error, commands.MissingPermissions):
            message = {
                'ru': 'У вас недостаточно прав для установки задержки в чате',
                'en': 'You do not have enough rights to set a chat delay',
                'uk': 'У вас недостатньо прав для встановлення затримки в чаті'
            }
            await inter.send(message[lang_server], ephemeral=True)
            return
        
        await inter.send("Что-то пошло не так, и тип этой ошибки просто невозможно определить", ephemeral=True)


    @commands.slash_command(description="🛡️ Снимает мут с пользователя")
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member = commands.Param(name='пользователь', description="Пользователь для снятия мута"), reason: str = commands.Param(None, name="причина", description="Причина снятия мута")):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        await member.edit(timeout=None, reason=reason)
        if lang_server == 'ru':
            embed = disnake.Embed(title="Снятие Мута", color=0x2F3136)
            embed.add_field(name="Пользователь:", value=f"{member.mention}", inline=False)
            embed.add_field(name="Причина:", value=f"`{reason}`", inline=False)
            embed.add_field(name="Модератор:", value=f"{inter.author.mention}", inline=False)
            embed.set_thumbnail(url=member.avatar)
        if lang_server == 'uk':
            embed = disnake.Embed(title="Зняття Мута", color=0x2F3136)
            embed.add_field(name="Користувач:", value=f"{member.mention}", inline=False)
            embed.add_field(name="Причина:", value=f"`{reason}`", inline=False)
            embed.add_field(name="Модератор:", value=f"{inter.author.mention}", inline=False)
            embed.set_thumbnail(url=member.avatar)
        if lang_server == 'en':
            embed = disnake.Embed(title="Unmute", color=0x2F3136)
            embed.add_field(name="User:", value=f"{member.mention}", inline=False)
            embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
            embed.add_field(name="Moderator:", value=f"{inter.author.mention}", inline=False)
            embed.set_thumbnail(url=member.avatar)
        await inter.send(embed=embed)

    @unmute.error
    async def unmute_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, disnake.Forbidden):
            return await inter.send("У бота недостаточно прав для снятия мута с пользователя", ephemeral=True)
        if isinstance(error, commands.BotMissingPermissions):
            return await inter.send("У бота недостаточно прав для снятия мута с пользователя", ephemeral=True)
        if isinstance(error, commands.MissingPermissions):
            return await inter.send("У вас недостаточно прав для снятия мута с пользователя", ephemeral=True)
        
        await inter.send("Что-то пошло не так, и тип этой ошибки просто невозможно определить", ephemeral=True)

    @commands.slash_command(description="🛡️ Модерация | Блокирует пользователя")
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(
            name='пользователь', 
            description="Пользователь для бана"), 
            reason: str = commands.Param("Отсутствует", name="причина", description="Причина бана")
                 ) -> None:
        await inter.response.defer()
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        await member.ban(reason=reason[:50])
        if lang_server == 'ru':
            embed = disnake.Embed(title="Бан", color=0x2F3136)
            embed.add_field(name="Пользователь:", value=f"{member.mention}", inline=False)
            embed.add_field(name="Причина:", value=f"`{reason[:50]}`", inline=False)
            embed.add_field(name="Модератор:", value=f"{inter.author.mention}", inline=False)
            embed.set_thumbnail(url=member.avatar)
        if lang_server == 'en':
            embed = disnake.Embed(title="Ban", color=0x2F3136)
            embed.add_field(name="User:", value=f"{member.mention}", inline=False)
            embed.add_field(name="Reason:", value=f"`{reason[:50]}`", inline=False)
            embed.add_field(name="Moderator:", value=f"{inter.author.mention}", inline=False)
            embed.set_thumbnail(url=member.avatar)
        if lang_server == 'uk':
            embed = disnake.Embed(title="Бан", color=0x2F3136)
            embed.add_field(name="Користувач:", value=f"{member.mention}", inline=False)
            embed.add_field(name="Причина:", value=f"`{reason[:50]}`", inline=False)
            embed.add_field(name="Модератор:", value=f"{inter.author.mention}", inline=False)
            embed.set_thumbnail(url=member.avatar)
        await inter.send(embed=embed)

    @ban.error
    async def ban_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, disnake.Forbidden):
            return await inter.send("У бота недостаточно прав для блокировки пользователя", ephemeral=True)
        if isinstance(error, commands.BotMissingPermissions):
            return await inter.send("У бота недостаточно прав для блокировки пользователя", ephemeral=True)
        if isinstance(error, commands.MissingPermissions):
            return await inter.send("У вас недостаточно прав для блокировки пользователя", ephemeral=True)
        
        await inter.send("Что-то пошло не так, и тип этой ошибки просто невозможно определить", ephemeral=True)

    @commands.slash_command(description="🛡️ Модерация | Снимает блокировку пользователя")
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, inter: disnake.ApplicationCommandInteraction, member: str = commands.Param(name="пользователь", description="ID пользователя которого вы хотите разбанить"), reason: str = commands.Param("Отсутствует", name="причина", description="Причина разбана")):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        try:
            user = disnake.Object(id=int(member))
        except:
            return await inter.send("Неизвестный пользователь! Используйте ID", ephemeral=True)
        try:
            await inter.guild.unban(user)
        except disnake.Forbidden:
            return await inter.send("У бота недостаточно прав для разблокировки пользователя", ephemeral=True)
        except disnake.NotFound:
            return await inter.send("Неизвестный пользователь! Возможно его нет в списке заблокированных пользователей", ephemeral=True)
        if lang_server == 'ru':
            embed = disnake.Embed(title="Разбан", color=0x2b2d31)
            embed.add_field(name="Пользователь:", value=f"<@!{member}>", inline=False)
            embed.add_field(name="Причина:", value=f"`{reason[:50]}`", inline=False)
            embed.add_field(name="Модератор:", value=f"{inter.author.mention}", inline=False)
        if lang_server == 'en':
            embed = disnake.Embed(title="Unbanned", color=0x2b2d31)
            embed.add_field(name="User:", value=f"<@!{member}>", inline=False)
            embed.add_field(name="Reason:", value=f"`{reason[:50]}`", inline=False)
            embed.add_field(name="Moderator:", value=f"{inter.author.mention}", inline=False)
        if lang_server == 'uk':
            embed = disnake.Embed(title="Розбан", color=0x2b2d31)
            embed.add_field(name="Користувач:", value=f"<@!{member}>", inline=False)
            embed.add_field(name="Причина:", value=f"`{reason[:50]}`", inline=False)
            embed.add_field(name="Модератор:", value=f"{inter.author.mention}", inline=False)
        await inter.send(embed=embed)
	
    @unban.autocomplete("пользователь")
    async def autounban(self, inter: disnake.ApplicationCommandInteraction, string: str):
        return [
		disnake.OptionChoice(
			name=f"{ban.user.name} ({ban.user.id})", 
			value=str(ban.user.id)
		) async for ban in inter.guild.bans(limit=25)
	]
    
    @unban.error
    async def unban_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, disnake.NotFound):
            return await inter.send("Неизвестный пользователь! Используйте ID", ephemeral=True)
        if isinstance(error, disnake.Forbidden):
            return await inter.send("У бота недостаточно прав для разблокировки пользователя", ephemeral=True)
        if isinstance(error, commands.BotMissingPermissions):
            return await inter.send("У бота недостаточно прав для разблокировки пользователя", ephemeral=True)
        if isinstance(error, commands.MissingPermissions):
            return await inter.send("У вас недостаточно прав для разблокировки пользователя", ephemeral=True)
        
        await inter.send("Что-то пошло не так, и тип этой ошибки просто невозможно определить", ephemeral=True)

def setup(bot):
    bot.add_cog(Moder(bot))

