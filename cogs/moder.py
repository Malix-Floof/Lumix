import disnake
import re
from disnake.ext import commands
from datetime import *
from db import SQLITE

db = SQLITE("database.db")


class Moder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'[ ОК ] Запущен moder.py')

    @commands.slash_command(description="🛡️ Модерация | Удаляет сообщения")
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def clear(self, inter, amount: commands.Range[int, 1, 100] = commands.Param(
                name="количество", description="Лимит для удаления сообщений: 100")):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        await inter.channel.purge(limit=amount)
        await inter.response.defer()
        if lang_server == 'ru':
            await inter.send(embed=disnake.Embed(description=f"Вы очистили `{amount}` сообщений", color=0x2b2d31))
        if lang_server == 'en':
            await inter.send(embed=disnake.Embed(description=f"You cleared `{amount}` messages", color=0x2b2d31))
        if lang_server == 'uk':
            await inter.send(embed=disnake.Embed(description=f"Ви очистили `{amount}` повідомлень", color=0x2b2d31))

    @clear.error
    async def clear_error(self, inter, error):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        if isinstance(error, commands.BotMissingPermissions):
            if lang_server == 'ru':
                return await inter.send("У бота недостаточно прав для отчистки сообщений", ephemeral=True)
            if lang_server == 'en':
                return await inter.send("The bot does not have enough rights to clear messages", ephemeral=True)
            if lang_server == 'uk':
                return await inter.send("У бота недостатньо прав для очищення повідомлень", ephemeral=True)
        if isinstance(error, commands.MissingPermissions):
            if lang_server == 'ru':
                return await inter.send("У вас недостаточно прав для отчистки сообщений", ephemeral=True)
            if lang_server == 'en':
                return await inter.send("You don't have enough rights to clear messages", ephemeral=True)
            if lang_server == 'uk':
                return await inter.send("У вас недостатньо прав для очищення повідомлень", ephemeral=True)
        if isinstance(error, commands.CommandError):
            if lang_server == 'ru':
                return await inter.send(f"Неизвестная ошибка: {error}", ephemeral=True)
            if lang_server == 'en':
                return await inter.send(f"Unknown error: {error}", ephemeral=True)
            if lang_server == 'uk':
                return await inter.send(f"Невідома помилка: {error}", ephemeral=True)

    @commands.slash_command(description="🛡️ Модерация | Даёт мут пользователю")
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    async def mute(self, inter,
                   member: disnake.Member = commands.Param(name='пользователь', description="Пользователь для мута"),
                   duration: str = commands.Param(name="время", description="1w, 1d, 15h, 30m, 30s"),
                   reason: str = commands.Param("Отсутствует", name="причина", description="Причина мута")):
        durations = duration.split()

        joke = ["Ха-ха, ну что у нас тут! Кажется, что-то пошло не по плану... Но подожди-ка, я вижу, этот участник, владелец сервера, просто неприступен! Он как незаглушимый супергерой, готовый отразить все мои попытки! Я чувствую себя просто как бедный злодей, пытающийся поймать моего супергеройского противника! Ха-ха-ха!",
                "Ой-ой, что-то пошло не по плану! Но стоп-стоп-стоп! У меня есть ощущение, что этот участник, владелец сервера, просто неприступен! Он как незаглушимый супергерой, готовый сразиться со всеми моими попытками! Я чувствую себя просто как злодей из комиксов, пытающийся поймать этого непобедимого героя! Ха-ха-ха!",
                "О нет, все идет не так... И я понимаю, этот участник, владелец сервера, непробиваемый. Он словно супергерой, готовый отразить все мои попытки. Мои усилия напрасны...",
                "Ох, ничего не получается! Он просто непокоримый материал, словно незаглушимый супергерой, который насмехается над моими попытками! Я злюсь и бушую от раздражения! Почему он так непробиваем?!"]

        if member.id == inter.guild.owner.id:
            await inter.send(choice(joke))

        if member.current_timeout is not None:
            await inter.send("Участник уже заглушен!", ephemeral=True)

        if member.top_role > inter.guild.me.top_role:
            await inter.send(f"**{inter.author.global_name}** чтобы заглушить участника, необходимо установить мою роль выше остальных ролей, так как роль участника имеет более высокий приоритет, чем моя. В противном случае я не смогу заглушить участника", ephemeral=True)

        if member.voice is not None:
            if member.voice.channel is not None:
                await member.move_to(None)

        for dur in durations:
            if not re.match(r'^\d+[wdhms]$', dur):
                raise commands.BadArgument('Неверный формат времени. Используйте формат: "1d 2h 3m"')

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

        weeks = total_seconds // (7 * 24 * 60 * 60)
        days = (total_seconds // (24 * 60 * 60)) % 7
        hours = (total_seconds // (60 * 60)) % 24
        minutes = (total_seconds // 60) % 60
        seconds = total_seconds % 60

        time_formatted = ""
        if weeks > 0:
            time_formatted += f"{weeks} недель "
        if days > 0:
            time_formatted += f"{days} дней "
        if hours > 0:
            time_formatted += f"{hours} часов "
        if minutes > 0:
            time_formatted += f"{minutes} минут "
        if seconds > 0:
            time_formatted += f"{seconds} секунд"
        await member.edit(timeout=total_seconds, reason=reason)
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        if lang_server == 'ru':
            embed = disnake.Embed(title="Мут", color=0x2F3136)
            embed.add_field(name="Пользователь:", value=f"{member.mention}", inline=False)
            embed.add_field(name="Время мута:", value=f"`{time_formatted}`", inline=False)
            embed.add_field(name="Причина:", value=f"`{reason}`", inline=False)
            embed.add_field(name="Модератор:", value=f"{inter.author.mention}", inline=False)
            embed.set_thumbnail(url=member.avatar.url)
        if lang_server == 'en':
            embed = disnake.Embed(title="Timeout", color=0x2F3136)
            embed.add_field(name="User:", value=f"{member.mention}", inline=False)
            embed.add_field(name="Timeout time:", value=f"`{duration}`", inline=False)
            embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
            embed.add_field(name="Мoderator:", value=f"{inter.author.mention}", inline=False)
            embed.set_thumbnail(url=member.avatar.url)
        if lang_server == 'uk':
            embed = disnake.Embed(title="Мут", color=0x2F3136)
            embed.add_field(name="Користувач:", value=f"{member.mention}", inline=False)
            embed.add_field(name="Час мута:", value=f"`{duration}`", inline=False)
            embed.add_field(name="Причина:", value=f"`{reason}`", inline=False)
            embed.add_field(name="Модератор:", value=f"{inter.author.mention}", inline=False)
            embed.set_thumbnail(url=member.avatar.url)
        await inter.send(embed=embed)

    @mute.error
    async def mute_error(self, inter, error):
        if isinstance(error, commands.BotMissingPermissions):
            await inter.send("У бота недостаточно прав для управления пользователями", ephemeral=True)
        if isinstance(error, commands.BotMissingPermissions):
            await inter.send("У вас недостаточно прав для управления пользователями", ephemeral=True)
        if isinstance(error, commands.BadArgument):
            await inter.send("Неверный формат времени. Используйте формат 1d 2h 3m через пробел", ephemeral=True)

    @commands.slash_command(description="🛡️ Модерация | Устанавливает медленный режим для текущего канала")
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, inter, seconds: commands.Range[int, 0, 21000] = commands.Param(name='секунды',
                                                                                            description="Задержка между сообщениями")):
        await inter.response.defer()
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        await inter.channel.edit(slowmode_delay=seconds)

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
            if lang_server == 'ru':
                embed = disnake.Embed(title="Медленный режим",
                                      description=f"Медленный режим был отключён",
                                      color=0x2b2d31)
            elif lang_server == 'en':
                embed = disnake.Embed(title="Slow mode",
                                      description=f"Slow mode has been disabled",
                                      color=0x2b2d31)
            elif lang_server == 'uk':
                embed = disnake.Embed(title="Повільний режим",
                                      description=f"Повільний режим був вимкнений",
                                      color=0x2b2d31)
        else:
            embed = disnake.Embed(title="Медленный режим",
                                  description=f"Медленный режим установлен на `{time_formatted}`",
                                  color=0x2b2d31)
            if lang_server == 'en':
                embed.title = "Slow mode"
                embed.description = f"Slow mode set to `{time_formatted}`"
            elif lang_server == 'uk':
                embed.title = "Повільний режим"
                embed.description = f"Повільний режим встановлено на `{time_formatted}`"

        await inter.send(embed=embed)

    @slowmode.error
    async def slowmode_error(self, inter, error):
        if isinstance(error, commands.BotMissingPermissions):
            await inter.send("У бота недостаточно прав для установки задержки в чате", ephemeral=True)
        if isinstance(error, commands.BotMissingPermissions):
            await inter.send("У вас недостаточно прав для установки задержки в чате", ephemeral=True)


    @commands.slash_command(description="🛡️ Модерация | Снимает мут с пользователя")
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, inter, member: disnake.Member = commands.Param(name='пользователь', description="Пользователь для снятия мута"), reason: str = commands.Param(None, name="причина", description="Причина снятия мута")):
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
            embed.set_thumbnail(url=member.avatar.url)
        await inter.send(embed=embed)

    @unmute.error
    async def unmute_error(self, inter, error):
        if isinstance(error, commands.BotMissingPermissions):
            await inter.send("У бота недостаточно прав для снятия мута с пользователя", ephemeral=True)
        if isinstance(error, commands.BotMissingPermissions):
            await inter.send("У вас недостаточно прав для снятия мута с пользователя", ephemeral=True)

    @commands.slash_command(description="🛡️ Модерация | Блокирует пользователя")
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, inter,
        member: disnake.User = commands.Param(
            name='пользователь', 
            description="Пользователь для бана"), 
            reason: str = commands.Param("Отсутствует", name="причина", description="Причина бана")):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        await member.ban(reason=reason)
        if lang_server == 'ru':
            embed = disnake.Embed(title="Бан", color=0x2F3136)
            embed.add_field(name="Пользователь:", value=f"{member.mention}", inline=False)
            embed.add_field(name="Причина:", value=f"`{reason}`", inline=False)
            embed.add_field(name="Модератор:", value=f"{inter.author.mention}", inline=False)
            embed.set_thumbnail(url=member.avatar)
        if lang_server == 'en':
            embed = disnake.Embed(title="Ban", color=0x2F3136)
            embed.add_field(name="User:", value=f"{member.mention}", inline=False)
            embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
            embed.add_field(name="Moderator:", value=f"{inter.author.mention}", inline=False)
            embed.set_thumbnail(url=member.avatar)
        if lang_server == 'uk':
            embed = disnake.Embed(title="Бан", color=0x2F3136)
            embed.add_field(name="Користувач:", value=f"{member.mention}", inline=False)
            embed.add_field(name="Причина:", value=f"`{reason}`", inline=False)
            embed.add_field(name="Модератор:", value=f"{inter.author.mention}", inline=False)
            embed.set_thumbnail(url=member.avatar)
        await inter.send(embed=embed)

    @ban.error
    async def ban_error(self, inter, error):
        if isinstance(error, commands.BotMissingPermissions):
            await inter.send("У бота недостаточно прав для блокировки пользователя", ephemeral=True)
        if isinstance(error, commands.BotMissingPermissions):
            await inter.send("У вас недостаточно прав для блокировки пользователя", ephemeral=True)

    @commands.slash_command(description="🛡️ Модерация | Снимает блокировку пользователя")
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, inter, member: str, reason: str = commands.Param("Отсутствует", name="причина", description="Причина разбана")):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        try:
            user = disnake.Object(id=member)
            await inter.guild.unban(user)
            if lang_server == 'ru':
                embed = disnake.Embed(title="Разбан", color=0x2b2d31)
                embed.add_field(name="Пользователь:", value=f"{member.mention}", inline=False)
                embed.add_field(name="Причина:", value=f"`{reason}`", inline=False)
                embed.add_field(name="Модератор:", value=f"{inter.author.mention}", inline=False)
            if lang_server == 'en':
                embed = disnake.Embed(title="Unbanned", color=0x2b2d31)
                embed.add_field(name="User:", value=f"{member.mention}", inline=False)
                embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
                embed.add_field(name="Moderator:", value=f"{inter.author.mention}", inline=False)
            if lang_server == 'uk':
                embed = disnake.Embed(title="Розбан", color=0x2b2d31)
                embed.add_field(name="Користувач:", value=f"{member.mention}", inline=False)
                embed.add_field(name="Причина:", value=f"`{reason}`", inline=False)
                embed.add_field(name="Модератор:", value=f"{inter.author.mention}", inline=False)
            await inter.send(embed=embed)
        except Exception as e:
            if lang_server == 'ru':
                await inter.send(embed=disnake.Embed(
                    title="Произошла ошибка при попытке разблокировать пользователя",
                    description=f"- Данный пользователь не имеет ограничений\n- Указан не известный пользователь\n- У вас недостаточно прав\n- У меня недостаточно прав", color=0x2b2d31))
            if lang_server == 'en':
                await inter.send(embed=disnake.Embed(
                    title="An error occurred while trying to unblock the user",
                    description=f"- This user has no restrictions\n- Unknown user specified\n- You do not have enough rights\n- I do not have enough rights", color=0x2b2d31))
            if lang_server == 'uk':
                await inter.send(embed=disnake.Embed(
                    title="Помилка при спробі розблокувати користувача",
                    description=f"- Даний користувач не має обмежень\n- Вказаний не відомий користувач\n- У вас недостатньо прав\n- У мене недостатньо прав", color=0x2b2d31))




def setup(bot):
    bot.add_cog(Moder(bot))
