import disnake
from disnake.ext import commands
from db import SQLITE
from datetime import datetime
import datetime

db = SQLITE("database.db")

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # [ ] Трибуна обновлена
    # [ ] Участник покинул канал трибуны
    # [ ] Участник зашел в канал трибуны
    # [ ] Трибуна закрыта
    # [ ] Трибуна открыта
    # [ ] Сообщения были очищены
    # [ ] Участник был размьючен
    # [ ] Участник был замьючен
    # [ ] Участник был разбанен
    # [ ] Участник был изгнан
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        lang_server = db.get(f"lang_{member.guild.id}") or "ru"
        logchannel = db.get(f"logchannel_{member.guild.id}")
        if logchannel is None:
            return
        
        channel = self.bot.get_channel(int(logchannel))
        if channel is None:
            return
        
        inviter_logs = await member.guild.audit_logs(limit=1).flatten()
        unkinver = {
            'ru': 'неизвестен',
            'en': 'unknown',
            'uk': 'невідомий'
        }
        inviter = inviter_logs[0].user.id if inviter_logs else unkinver[lang_server]
        
        if lang_server == 'ru':
            if member.bot:
                embed = disnake.Embed(description=f"Бот {member.mention} (`{member.name}`) был добавлен пользователем <@{inviter}>", timestamp=datetime.datetime.now(),  color=0x2b2d31)
                embed.add_field(name="Дата регистрации:", value=f'{disnake.utils.format_dt(member.created_at, "D")} ({disnake.utils.format_dt(member.created_at, "R")})')
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
            else:
                embed = disnake.Embed(description=f"Участник {member.mention} (`{member.name}`) присоединился к серверу", timestamp=datetime.datetime.now(),  color=0x2b2d31)
                embed.add_field(name="Дата регистрации:", value=f'{disnake.utils.format_dt(member.created_at, "D")} ({disnake.utils.format_dt(member.created_at, "R")})')
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
        if lang_server == 'uk':
            if member.bot:
                embed = disnake.Embed(description=f"Бот {member.mention} (`{member.name}`) був доданий користувачем <@{inviter}>", timestamp=datetime.datetime.now(),  color=0x2b2d31)
                embed.add_field(name="Дата реєстрації:", value=f'{disnake.utils.format_dt(member.created_at, "D")} ({disnake.utils.format_dt(member.created_at, "R")})')
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
            else:
                embed = disnake.Embed(description=f"Учасник {member.mention} (`{member.name}`) приєднався до сервера", timestamp=datetime.datetime.now(),  color=0x2b2d31)
                embed.add_field(name="Дата реєстрації:", value=f'{disnake.utils.format_dt(member.created_at, "D")} ({disnake.utils.format_dt(member.created_at, "R")})')
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
        if lang_server == 'en':
            if member.bot:
                embed = disnake.Embed(description=f"Bot {member.mention} (`{member.name}`) was added by user <@{inviter}>", timestamp=datetime.datetime.now(),  color=0x2b2d31)
                embed.add_field(name="Date of registration:", value=f'{disnake.utils.format_dt(member.created_at, "D")} ({disnake.utils.format_dt(member.created_at, "R")})')
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
            else:
                embed = disnake.Embed(description=f"Member {member.mention} (`{member.name}`) has joined the server", timestamp=datetime.datetime.now(),  color=0x2b2d31)
                embed.add_field(name="Date of registration:", value=f'{disnake.utils.format_dt(member.created_at, "D")} ({disnake.utils.format_dt(member.created_at, "R")})')
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        lang_server = db.get(f"lang_{member.guild.id}") or "ru"
        logchannel = db.get(f"logchannel_{member.guild.id}")
        if logchannel is None:
            return
        channel = self.bot.get_channel(int(logchannel))
        if channel is None:
            return
        roles = [role.mention for role in reversed(member.roles[1:])]
        if len(roles) > 15:
            if lang_server == 'ru':
                roles = roles[:15] + [f"\nи еще {len(roles) - 15} ролей..."]
            if lang_server == 'en':
                roles = roles[:15] + [f"\nand {len(roles) - 15} more roles..."]
            if lang_server == 'uk':
                roles = roles[:15] + [f"\nта ще {len(roles) - 15} ролей..."]

        if lang_server == 'ru':
            if member.bot:
                embed = disnake.Embed(description=f"Бот {member.mention} (`{member.name}`) покинул сервер", timestamp=datetime.datetime.now(),  color=0x2b2d31)
                embed.add_field(name="Роли:", value=' '.join(roles))
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
            else:
                embed = disnake.Embed(description=f"Участник {member.mention} (`{member.name}`) покинул(-а) сервер", timestamp=datetime.datetime.now(),  color=0x2b2d31)
                embed.add_field(name="Роли:", value=' '.join(roles))
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
        if lang_server == 'en':
            if member.bot:
                embed = disnake.Embed(description=f"Bot {member.mention} (`{member.name}`) left the server", timestamp=datetime.datetime.now(),  color=0x2b2d31)
                embed.add_field(name="Roles:", value=' '.join(roles))
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
            else:
                embed = disnake.Embed(description=f"Member {member.mention} (`{member.name}`) left the server", timestamp=datetime.datetime.now(),  color=0x2b2d31)
                embed.add_field(name="Roles:", value=' '.join(roles))
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
        if lang_server == 'uk':
            if member.bot:
                embed = disnake.Embed(description=f"Бот {member.mention} (`{member.name}`) залишив сервер", timestamp=datetime.datetime.now(),  color=0x2b2d31)
                embed.add_field(name="Ролі:", value=' '.join(roles))
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
            else:
                embed = disnake.Embed(description=f"Учасник {member.mention} (`{member.name}`) залишив сервер", timestamp=datetime.datetime.now(),  color=0x2b2d31)
                embed.add_field(name="Ролі:", value=' '.join(roles))
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        lang_server = db.get(f"lang_{guild.id}") or "ru"
        logchannel = db.get(f"logchannel_{guild.id}")
        if logchannel is None:
            return
        channel = self.bot.get_channel(int(logchannel))
        if channel is None:
            return
        if user.bot:
        	return
        if lang_server == 'ru':
            embed = disnake.Embed(description=f"Участник {user.mention} (`{user.name}`) был забанен на сервере", timestamp=datetime.datetime.now(), color=0x2b2d31)
        if lang_server == 'en':
            embed = disnake.Embed(description=f"Member {user.mention} (`{user.name}`) has been banned from the server", timestamp=datetime.datetime.now(), color=0x2b2d31)
        if lang_server == 'uk':
            embed = disnake.Embed(description=f"Учасник {user.mention} (`{user.name}`) був забанен на сервері", timestamp=datetime.datetime.now(), color=0x2b2d31)
        roles = [role.mention for role in reversed(user.roles[1:])]
        if len(roles) > 15:
            if lang_server == 'ru':
                roles = roles[:15] + [f"\nи еще {len(roles) - 15} ролей..."]
            if lang_server == 'en':
                roles = roles[:15] + [f"\nand {len(roles) - 15} more roles..."]
            if lang_server == 'uk':
                roles = roles[:15] + [f"\nта ще {len(roles) - 15} ролей..."]
        if roles is None:
            roles = {
                'ru': 'Отсутствуют',
                'en': 'None',
                'uk': 'Відсутні'
            }[lang_server]
            
        if lang_server == 'ru':
            embed.add_field(name="Роли:", value=' '.join(roles))
        if lang_server == 'en':
            embed.add_field(name="Roles:", value=' '.join(roles))
        if lang_server == 'uk':
            embed.add_field(name="Ролі:", value=' '.join(roles))
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"ID: {user.id}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        lang_server = db.get(f"lang_{guild.id}") or "ru"
        logchannel = db.get(f"logchannel_{guild.id}")
        if logchannel is None:
            return
        
        channel = self.bot.get_channel(int(logchannel))
        if channel is None:
            return
        
        if lang_server == 'ru':
            embed = disnake.Embed(description=f"Участник {user.mention} (`{user.name}`) был разбанен на сервере", timestamp=datetime.datetime.now(), color=0x2b2d31)
        if lang_server == 'en':
            embed = disnake.Embed(description=f"Member {user.mention} (`{user.name}`) has been unbanned from the server", timestamp=datetime.datetime.now(), color=0x2b2d31)
        if lang_server == 'uk':
            embed = disnake.Embed(description=f"Учасник {user.mention} (`{user.name}`) був розбанений на сервері", timestamp=datetime.datetime.now(), color=0x2b2d31)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"ID: {user.id}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        lang_server = db.get(f"lang_{before.guild.id}") or "ru"
        logchannel = db.get(f"logchannel_{before.guild.id}")
        if logchannel is None:
            return
        channel = self.bot.get_channel(int(logchannel))
        if channel is None:
            return
        
        if before.nick != after.nick:
            if lang_server == 'ru':
                embed = disnake.Embed(description=f"Никнейм пользователя `{after.nick}` был обновлён", timestamp=datetime.datetime.now(), color=0x2b2d31)
                embed.add_field(name='До:',value=f'```\n{before.nick}\n```', inline=False)
                embed.add_field(name='После:',value=f'```\n{after.nick}\n```', inline=False)
            if lang_server == 'en':
                embed = disnake.Embed(description=f"Nickname of user `{after.nick}` has been updated", timestamp=datetime.datetime.now(), color=0x2b2d31)
                embed.add_field(name='Before:',value=f'```\n{before.nick}\n```', inline=False)
                embed.add_field(name='After:',value=f'```\n{after.nick}\n```', inline=False)
            if lang_server == 'uk':
                embed = disnake.Embed(description=f"Нікнейм користувача `{after.nick}` було оновлено", timestamp=datetime.datetime.now(), color=0x2b2d31)
                embed.add_field(name='До:',value=f'```\n{before.nick}\n```', inline=False)
                embed.add_field(name='Після:',value=f'```\n{after.nick}\n```', inline=False)
            embed.set_footer(text=f"ID: {before.id}")
            embed.set_thumbnail(url=before.display_avatar.url)
            await channel.send(embed=embed)

        if before.roles != after.roles:
            added_roles = [f"<@&{role.id}>" for role in after.roles if role not in before.roles]
            removed_roles = [f"<@&{role.id}>" for role in before.roles if role not in after.roles]

            if added_roles:
                for role in added_roles:
                    roles = role
                if lang_server == 'ru':
                    embed = disnake.Embed(title='Роли участника обновлены', description = f'Участнику {before.mention} (`{before.name}`) добавлены роли: {roles}',timestamp=datetime.datetime.now(),  color=0x2b2d31)
                if lang_server == 'en':
                    embed = disnake.Embed(title='Member roles updated', description = f'Member {before.mention} (`{before.name}`) has roles added: {roles}',timestamp=datetime.datetime.now(),  color=0x2b2d31)
                if lang_server == 'uk':
                    embed = disnake.Embed(title='Ролі учасника оновлено', description = f'Учаснику {before.mention} (`{before.name}`) додано ролі: {roles}',timestamp=datetime.datetime.now(),  color=0x2b2d31)

            if removed_roles:
                for role in removed_roles:
                    roles = role
                if lang_server == 'ru':
                    embed = disnake.Embed(title='Роли участника обновлены', description = f'Участнику {before.mention} (`{before.name}`) убрали роли: {roles}',timestamp=datetime.datetime.now(),  color=0x2b2d31)
                if lang_server == 'en':
                    embed = disnake.Embed(title='Member roles updated', description = f'Member {before.mention} (`{before.name}`) has had their roles removed: {roles}',timestamp=datetime.datetime.now(),  color=0x2b2d31)
                if lang_server == 'uk':
                    embed = disnake.Embed(title='Ролі учасника оновлено', description = f'Учаснику {before.mention} (`{before.name}`) забрали ролі: {roles}',timestamp=datetime.datetime.now(),  color=0x2b2d31)

            embed.set_thumbnail(url=before.display_avatar.url)
            embed.set_footer(text=f"ID: {before.id}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        lang_server = db.get(f"lang_{before.guild.id}") or "ru"
        logchannel = db.get(f"logchannel_{before.guild.id}")
        if logchannel is None:
            return
        channel = self.bot.get_channel(int(logchannel))
        if channel is None:
            return
        
        if before.content == after.content:
            return
        if lang_server == 'ru':
            embed = disnake.Embed(description=f"[Сообщение]({after.jump_url}) было отредактировано", timestamp=datetime.datetime.now(), color=0x2b2d31)
            embed.add_field(name='До:', value=f'```\n{before.content}\n```', inline=False)
            embed.add_field(name='После:', value=f'```\n{after.content}\n```', inline=False)
            embed.add_field(name='Автор:', value=f'{before.author.mention} (`{before.author.name}`)', inline=True)
            embed.add_field(name='Канал:', value=f'{before.channel.mention} (`{before.channel.name}`)', inline=True)
            embed.set_footer(text=f"ID: {before.id}")
        if lang_server == 'en':
            embed = disnake.Embed(description=f"[Post]({after.jump_url}) has been edited", timestamp=datetime.datetime.now(), color=0x2b2d31)
            embed.add_field(name='Before:', value=f'```\n{before.content}\n```', inline=False)
            embed.add_field(name='After:', value=f'```\n{after.content}\n```', inline=False)
            embed.add_field(name='Author:', value=f'{before.author.mention} (`{before.author.name}`)', inline=True)
            embed.add_field(name='Channel:', value=f'{before.channel.mention} (`{before.channel.name}`)', inline=True)
            embed.set_footer(text=f"ID: {before.id}")
        if lang_server == 'uk':
            embed = disnake.Embed(description=f"[Повідомлення]({after.jump_url}) було відредаговано", timestamp=datetime.datetime.now(), color=0x2b2d31)
            embed.add_field(name='До:', value=f'```\n{before.content}\n```', inline=False)
            embed.add_field(name='Після:', value=f'```\n{after.content}\n```', inline=False)
            embed.add_field(name='Автор:', value=f'{before.author.mention} (`{before.author.name}`)', inline=True)
            embed.add_field(name='Канал:', value=f'{before.channel.mention} (`{before.channel.name}`)', inline=True)
            embed.set_footer(text=f"ID: {before.id}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        lang_server = db.get(f"lang_{message.guild.id}") or "ru"
        logchannel = db.get(f"logchannel_{message.guild.id}")
        if logchannel is None:
            return
        channel = self.bot.get_channel(int(logchannel))
        if channel is None:
            return
        message_content = message.content
        if message_content == '':
            return
        if len(message_content) > 1024:
            with open('message.txt', 'w', encoding='utf-8') as file:
                file.write(message_content)
            file = disnake.File("message.txt")
            if lang_server == 'ru':
                embed = disnake.Embed(description=f"Сообщение было удалено", color=0x2b2d31)
                embed.add_field(name='Автор:', value=f'{message.author.mention} (`{message.author.name}`)', inline=True)
                embed.add_field(name='Длина сообщения:', value=f'`{len(message.content)}` символов', inline=True)
                embed.add_field(name='Канал:', value=f'{message.channel.mention} (`{message.channel.name}`)', inline=True)
            if lang_server == 'en':
                embed = disnake.Embed(description=f"Post has been deleted", color=0x2b2d31)
                embed.add_field(name='Author:', value=f'{message.author.mention} (`{message.author.name}`)', inline=True)
                embed.add_field(name='Message length:', value=f'`{len(message.content)}` characters', inline=True)
                embed.add_field(name='Channel:', value=f'{message.channel.mention} (`{message.channel.name}`)', inline=True)
            if lang_server == 'uk':
                embed = disnake.Embed(description=f"Повідомлення було видалено", color=0x2b2d31)
                embed.add_field(name='Автор:', value=f'{message.author.mention} (`{message.author.name}`)', inline=True)
                embed.add_field(name='Довжина повідомлення:', value=f'`{len(message.content)}` символів', inline=True)
                embed.add_field(name='Канал:', value=f'{message.channel.mention} (`{message.channel.name}`)', inline=True)
            await channel.send(embed=embed, file=file)
        if len(message_content) < 1024:
            text = message.content.replace("`", "")
            if lang_server == 'ru':
                embed = disnake.Embed(description=f"Сообщение было удалено", color=0x2b2d31)
                embed.add_field(name='Удалённое сообщение:', value=f'```\n{text}\n```', inline=False)
                embed.add_field(name='Автор:', value=f'{message.author.mention} (`{message.author.name}`)', inline=True)
                embed.add_field(name='Канал:', value=f'{message.channel.mention} (`{message.channel.name}`)', inline=True)
            if lang_server == 'en':
                embed = disnake.Embed(description=f"Post has been deleted", color=0x2b2d31)
                embed.add_field(name='Deleted message:', value=f'```\n{text}\n```', inline=False)
                embed.add_field(name='Author:', value=f'{message.author.mention} (`{message.author.name}`)', inline=True)
                embed.add_field(name='Channel:', value=f'{message.channel.mention} (`{message.channel.name}`)', inline=True)
            if lang_server == 'uk':
                embed = disnake.Embed(description=f"Повідомлення було видалено", color=0x2b2d31)
                embed.add_field(name='Віддалене повідомлення:', value=f'```\n{text}\n```', inline=False)
                embed.add_field(name='Автор:', value=f'{message.author.mention} (`{message.author.name}`)', inline=True)
                embed.add_field(name='Канал:', value=f'{message.channel.mention} (`{message.channel.name}`)', inline=True)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        lang_server = db.get(f"lang_{member.guild.id}") or "ru"
        logchannel = db.get(f"logchannel_{member.guild.id}")

        if logchannel is None:
            return

        channel = self.bot.get_channel(int(logchannel))
        if channel is None:
            return

        lang_texts = {
            'ru': {
                'join': ("Участник присоединился к голосовому каналу",
                         "присоединился к голосовому каналу"),
                'leave': ("Участник вышел из голосового канала",
                          "покинул голосовой канал"),
                'move': ("Участник перешёл в другой голосовой канал",
                         "перешёл в голосовой канал")
            },
            'en': {
                'join': ("Participant joined the voice channel",
                         "joined voice channel"),
                'leave': ("The participant left the voice channel",
                          "left the voice channel"),
                'move': ("Participant moved to another voice channel",
                         "switched to voice channel")
            },
            'uk': {
                'join': ("Учасник приєднався до голосового каналу",
                         "приєднався до голосового каналу"),
                'leave': ("Учасник вийшов із голосового каналу",
                          "залишив голосовий канал"),
                'move': ("Учасник перейшов до іншого голосового каналу",
                         "перейшов у голосовий канал")
            }
        }

        action = None
        description = None

        if before.channel is None and after.channel is not None:
            action = 'join'
            description = f"{member.mention} (`{member.name}`) {lang_texts[lang_server][action][1]} {after.channel.mention}"
        elif before.channel is not None and after.channel is None:
            action = 'leave'
            description = f"{member.mention} (`{member.name}`) {lang_texts[lang_server][action][1]} {before.channel.mention}"
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            action = 'move'
            description = f"{member.mention} (`{member.name}`) {lang_texts[lang_server][action][1]} {after.channel.mention}"

        if action:
            embed = disnake.Embed(
                title=lang_texts[lang_server][action][0],
                description=description,
                timestamp=datetime.datetime.now(),
                color=0x2b2d31        )
            embed.set_footer(text=f"ID: {member.id}")
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        lang_server = db.get(f"lang_{role.guild.id}") or "ru"
        logchannel = db.get(f"logchannel_{role.guild.id}")
        if logchannel is None:
            return
        channel = self.bot.get_channel(int(logchannel))
        if channel is None:
            return 
        
        if lang_server == 'ru':
            embed = disnake.Embed(title="Роль создана", description=f"Создана роль {role.mention}", timestamp=datetime.datetime.now(), color=0x2b2d31)
            embed.set_footer(text=f"ID роли: {role.id}")
        if lang_server == 'en':
            embed = disnake.Embed(title="Role created", description=f"Role created {role.mention}", timestamp=datetime.datetime.now(), color=0x2b2d31)
            embed.set_footer(text=f"Role ID: {role.id}")
        if lang_server == 'uk':
            embed = disnake.Embed(title="Роль створена", description=f"Створено роль {role.mention}", timestamp=datetime.datetime.now(), color=0x2b2d31)
            embed.set_footer(text=f"ID ролі: {role.id}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        lang_server = db.get(f"lang_{role.guild.id}") or "ru"
        logchannel = db.get(f"logchannel_{role.guild.id}")
        if logchannel is None:
            return
        channel = self.bot.get_channel(int(logchannel))
        if channel is None:
            return
        if lang_server == 'ru':
            embed = disnake.Embed(title="Роль удалена", description=f"Удалена роль `@{role.name}`", timestamp=datetime.datetime.now(), color=0x2b2d31)
            embed.set_footer(text=f"ID роли: {role.id}")
            await channel.send(embed=embed)
        if lang_server == 'en':
            embed = disnake.Embed(title="Role removed", description=f"Removed role `@{role.name}`", timestamp=datetime.datetime.now(), color=0x2b2d31)
            embed.set_footer(text=f"Role ID: {role.id}")
            await channel.send(embed=embed)
        if lang_server == 'uk':
            embed = disnake.Embed(title="Роль видалена", description=f"Вилучена роль `@{role.name}`", timestamp=datetime.datetime.now(), color=0x2b2d31)
            embed.set_footer(text=f"ID ролі: {role.id}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, chann):
        lang_server = db.get(f"lang_{chann.guild.id}") or "ru"
        logchannel = db.get(f"logchannel_{chann.guild.id}")
        if logchannel is None:
            return
        channel = self.bot.get_channel(int(logchannel))
        if channel is None:
            return
        if lang_server == 'ru':
            embed = disnake.Embed(title='Канал был создан', description = f'Канал {chann.mention} был создан', timestamp=datetime.datetime.now(), color=0x2b2d31)
            embed.set_footer(text=f"ID канала: {channel.id}")
        if lang_server == 'en':
            embed = disnake.Embed(title='The channel has been created', description = f'Channel {chann.mention} has been created', timestamp=datetime.datetime.now(), color=0x2b2d31)
            embed.set_footer(text=f"Channel ID: {channel.id}")
        if lang_server == 'uk':
            embed = disnake.Embed(title='Канал було створено', description = f'Канал {chann.mention} був створений', timestamp=datetime.datetime.now(), color=0x2b2d31)
            embed.set_footer(text=f"ID каналу: {channel.id}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, chann):
        lang_server = db.get(f"lang_{chann.guild.id}") or "ru"
        logchannel = db.get(f"logchannel_{chann.guild.id}")
        if logchannel is None:
            return
        channel = self.bot.get_channel(int(logchannel))
        if channel is None:
            return
        if lang_server == 'ru':
            embed = disnake.Embed(title='Канал был удалён', description = f'Канал `#{chann.name}` был удалён', timestamp=datetime.datetime.now(), color=0x2b2d31)
        if lang_server == 'en':
            embed = disnake.Embed(title='The channel has been deleted', description = f'Channel `#{chann.name}` has been deleted', timestamp=datetime.datetime.now(), color=0x2b2d31)
        if lang_server == 'uk':
            embed = disnake.Embed(title='Канал був вилучений', description = f'Канал `#{chann.name}` був вилучений', timestamp=datetime.datetime.now(), color=0x2b2d31)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        
        lang_server = db.get(f"lang_{after.guild.id}") or "ru"
        logchannel = db.get(f"logchannel_{after.guild.id}")
        if logchannel is None:
            return
        channel = self.bot.get_channel(int(logchannel))
        if channel is None:
            return
        
        embed = None

        if before.name != after.name:
            if lang_server == 'ru':
                embed = disnake.Embed(title='Канал был обновлён', description=f'Канал `#{before.name}` был переименован в `#{after.name}` ({after.mention})', 
                    timestamp=datetime.datetime.now(), color=0x2b2d31)
            if lang_server == 'en':
                embed = disnake.Embed(title='The channel has been updated', description=f'Channel `#{before.name}` has been renamed to `#{after.name}` ({after.mention})', 
                    timestamp=datetime.datetime.now(), color=0x2b2d31)
            if lang_server == 'uk':
                embed = disnake.Embed(title='Канал було оновлено', description=f'Канал `#{before.name}` був перейменований на `#{after.name}` ({after.mention})', 
                    timestamp=datetime.datetime.now(), color=0x2b2d31)
            return await channel.send(embed=embed)

        if before.type == disnake.ChannelType.voice or disnake.ChannelType.category:
            return

        if before.topic != "" and after.topic == "":
            if lang_server == 'ru':
                embed = disnake.Embed(title='Канал был обновлён', description=f'Тема канала {after.mention} была убрана', timestamp=datetime.datetime.now(), color=0x2b2d31)
                embed.add_field(name='Тема:', value=f'```\n{before.topic}\n```', inline=False)
            if lang_server == 'en':
                embed = disnake.Embed(title='The channel has been updated', description=f'Channel topic {after.mention} was removed', timestamp=datetime.datetime.now(), color=0x2b2d31)
                embed.add_field(name='Topic:', value=f'```\n{before.topic}\n```', inline=False)
            if lang_server == 'uk':
                embed = disnake.Embed(title='Канал було оновлено', description=f'Тему каналу {after.mention} була прибрана', timestamp=datetime.datetime.now(), color=0x2b2d31)
                embed.add_field(name='Тему:', value=f'```\n{before.topic}\n```', inline=False)
            return await channel.send(embed=embed)
            
        if before.topic == "" and after.topic != "":
            if lang_server == 'ru':
                embed = disnake.Embed(title='Канал был обновлён', description=f'Тема канала {after.mention} была добавлена', timestamp=datetime.datetime.now(), color=0x2b2d31)
                embed.add_field(name='Тема:', value=f'```\n{after.topic}\n```', inline=False)
            if lang_server == 'en':
                embed = disnake.Embed(title='The channel has been updated', description=f'Channel topic {after.mention} has been added', timestamp=datetime.datetime.now(), color=0x2b2d31)
                embed.add_field(name='Topic:', value=f'```\n{after.topic}\n```', inline=False)
            if lang_server == 'uk':
                embed = disnake.Embed(title='Канал було оновлено', description=f'Тему каналу {after.mention} було додано', timestamp=datetime.datetime.now(), color=0x2b2d31)
                embed.add_field(name='Тему:', value=f'```\n{after.topic}\n```', inline=False)
            return await channel.send(embed=embed)
            
        if before.topic != after.topic:
            if lang_server == 'ru':
                embed = disnake.Embed(title='Канал был обновлён', description=f'Тема канала {after.mention} была изменена', timestamp=datetime.datetime.now(), color=0x2b2d31)
                embed.add_field(name='До:', value=f'```\n{before.topic}\n```', inline=False)
                embed.add_field(name='После:', value=f'```\n{after.topic}\n```', inline=False)
            if lang_server == 'en':
                embed = disnake.Embed(title='The channel has been updated', description=f'The {after.mention} channel theme has been changed', timestamp=datetime.datetime.now(), color=0x2b2d31)
                embed.add_field(name='Before:', value=f'```\n{before.topic}\n```', inline=False)
                embed.add_field(name='After:', value=f'```\n{after.topic}\n```', inline=False)
            if lang_server == 'uk':
                embed = disnake.Embed(title='Канал було оновлено', description=f'Тему каналу {after.mention} було змінено', timestamp=datetime.datetime.now(), color=0x2b2d31)
                embed.add_field(name='До:', value=f'```\n{before.topic}\n```', inline=False)
                embed.add_field(name='Після:', value=f'```\n{after.topic}\n```', inline=False)
            await channel.send(embed=embed)

    @commands.slash_command(description='🔧 Утилиты | Установить канал для логов')
    @commands.has_permissions(view_audit_log=True)
    async def setlogchannel(self, inter, channel: disnake.TextChannel):
        logchannel = db.set(f"logchannel_{inter.guild.id}", f"{channel.id}")
        await inter.send(f"Теперь логи сервера будут приходить в установленный канал: {channel.mention}", ephemeral=True)

    @setlogchannel.error
    async def setlogchannel_error(self, inter):
        if isinstance(error, commands.MissingPermissions):
            await inter.send("У вас должно быть право на просмотр журнала сервера что бы установить канал для логирования", ephemeral=True)


def setup(bot):
    bot.add_cog(Logs(bot))
