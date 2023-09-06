import disnake
import aiohttp
from random import randint, choice
from disnake.ext import commands
from db import SQLITE
from googletrans import Translator

db = SQLITE("database.db")

async def translator(word):
        translator = Translator()
        result = translator.translate(word, dest = 'ru')
        return result.text

class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False


    @commands.slash_command(description=f"📌 Информация | Показывает информацию об участнике")
    async def user(self, inter, target: disnake.Member = commands.Param(None, name="user", description="Участник")):
        try:
            await inter.response.defer()
            member = target or inter.user
            lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
            rep = db.get(f"repytation_{member.id}") or 0
            if member.premium_since:
                bdate = disnake.utils.format_dt(member.premium_since, 'D')
                if lang_server == 'ru':
                    boost = f"<:boost:1069623063769006200> бустит данный сервер с {bdate}"
                if lang_server == 'en':
                    boost = f"<:boost:1069623063769006200> boost this server with {bdate}"
                if lang_server == 'uk':
                    boost = f"<:boost:1069623063769006200> бустит даний сервер з {bdate}"
            else:
                boost = " "
            if lang_server == 'ru':
                status = {
                    'dnd': '<:dnd:1069621956552446102> Не беспокоить',
                    'online': '<:online:1069622306902659102> В сети',
                    'idle': '<:inactive:1069621996834541598> Неактивен',
                    'offline': '<:offline:1069621834577874977> Не в сети'
                }
            if lang_server == 'en':
                status = {
                    'dnd': '<:dnd:1069621956552446102> Do not disturb',
                    'online': '<:online:1069622306902659102> Online',
                    'idle': '<:inactive:1069621996834541598> Inactive',
                    'offline': '<:offline:1069621834577874977> Offline'
                }
            if lang_server == 'uk':
                status = {
                    'dnd': '<:dnd:1069621956552446102> Не турбувати',
                    'online': '<:online:1069622306902659102> В мережі',
                    'idle': '<:inactive:1069621996834541598> Неактивний',
                    'offline': '<:offline:1069621834577874977> Не в мережі'
                }
            badges = {
                "staff": "<:staff:812692120049156127>",
                "partner": "<:partner:812692120414322688>",
                "hypesquad": "<:hypesquad_events:812692120358879262>",
                "bug_hunter": "<:bug_hunter:812692120313266176>",
                "hypesquad_bravery": "<:bravery:1069623689290711080>",
                "hypesquad_brilliance": "<:brilliance:1069623643933507655>",
                "hypesquad_balance": "<:balance:1069623562434002977>",
                "verified_bot_developer": "<:verified_bot_developer:812692120133042178>",
                "active_developer": "<:active_dev:1073501273992732733>",
                "premium_promo_dismissed": "<:nitro:1121417787156471890>"
            }
            roles = [role.mention for role in reversed(member.roles[1:])]
            if len(roles) > 15:
                if lang_server == 'ru':
                    roles = roles[:15] + ["\nи еще {} ролей...".format(len(roles) - 15)]
                if lang_server == 'en':
                    roles = roles[:15] + ["\nand {} more roles...".format(len(roles) - 15)]
                if lang_server == 'uk':
                    roles = roles[:15] + ["\nта ще {} ролей...".format(len(roles) - 15)]
            user = await self.bot.fetch_user(member.id)
            badge_string = ' '.join(badges[pf.name] for pf in member.public_flags.all() if pf.name in badges)
            embed = disnake.Embed(description=f"{boost}", color=member.top_role.color.value)
            activities = []
            for activity in member.activities:
                if isinstance(activity, disnake.Spotify):
                    activities.append(
                        "<:Spotify:1069625439531847771> **Spotify:**\n"
                        f"> Трек: `{activity.title}`\n"
                        f"> Автор: `{activity.artist}`\n"
                        f"> Длительность: `{str(activity.duration)[:7]}`"
                    )
                elif isinstance(activity, disnake.CustomActivity):
                    pass
                elif activity.name == "Visual Studio Code":
                    activities.append(f"**{activity.name}**")
                elif activity.name == "Minecraft":
                    activities.append(f":minecraft: **Играет в {activity.name}**")
                else:
                    activities.append(activity.name)
            if lang_server == 'ru':
                activities.append("Информация отсутствует") if not activities else None
            if lang_server == 'en':
                activities.append("Information is absent") if not activities else None
            if lang_server == 'uk':
                activities.append("Інформація відсутня") if not activities else None

            if lang_server == 'ru':
                embed.set_author(name=f"Информация о {member.name}", icon_url=member.display_avatar.url)
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.add_field(name=f'Никнейм:', value=f'{member.global_name}', inline=True)
                embed.add_field(name='Статус:', value=status[str(member.status)], inline=True)
                embed.add_field(name=f'Роли: [{len(member.roles) - 1}]', value=' '.join(roles), inline=False)
                embed.add_field(name='Аккаунт создан:', value=f'{disnake.utils.format_dt(member.created_at, "R")}', inline=True)
                embed.add_field(name='Зашёл на сервер:', value=f'{disnake.utils.format_dt(member.joined_at, "R")}', inline=True)
                embed.add_field(name=f'Значки профиля:', value=f'{badge_string}', inline=True)
                embed.add_field(name=f'Репутация:', value=f"{rep} Единиц репутации", inline=True)
                embed.add_field(name=f'Активности:', value='\n'.join(activities), inline=True)
                embed.set_image(url=user.banner)
                embed.set_footer(text=f"Пользовательский ID: {member.id}")
            if lang_server == 'en':
                embed.set_author(name=f"Information about {member.name}", icon_url=member.display_avatar.url)
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.add_field(name=f'Nickname:', value=f'{member.global_name}', inline=True)
                embed.add_field(name='Status:', value=status[str(member.status)], inline=True)
                embed.add_field(name=f'Roles: [{len(member.roles) - 1}]', value=' '.join(roles), inline=False)
                embed.add_field(name='Account created:', value=f'{disnake.utils.format_dt(member.created_at, "R")}', inline=True)
                embed.add_field(name='Went to the server:', value=f'{disnake.utils.format_dt(member.joined_at, "R")}', inline=True)
                embed.add_field(name=f'Badges:', value=f'{badge_string}', inline=True)
                embed.add_field(name=f'Reputation:', value=f"{rep} Reputation amount", inline=True)
                embed.add_field(name=f'Activities:', value='\n'.join(activities), inline=True)
                embed.set_image(url=user.banner)
                embed.set_footer(text=f"User ID: {member.id}")
            if lang_server == 'uk':
                embed.set_author(name=f"Інформація про {member.name}", icon_url=member.display_avatar.url)
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.add_field(name=f'Нікнейм', value=f'{member.global_name}', inline=True)
                embed.add_field(name='Статус:', value=status[str(member.status)], inline=True)
                embed.add_field(name=f'Ролі: [{len(member.roles) - 1}]', value=' '.join(roles), inline=False)
                embed.add_field(name='Обліковий запис створено:', value=f'{disnake.utils.format_dt(member.created_at, "R")}', inline=True)
                embed.add_field(name='Зайшов на сервер:', value=f'{disnake.utils.format_dt(member.joined_at, "R")}', inline=True)
                embed.add_field(name=f'Піктограми профілю:', value=f'{badge_string}', inline=True)
                embed.add_field(name=f'Репутація:', value=f"{rep} Единиц репутации", inline=True)
                embed.add_field(name=f'Активності:', value='\n'.join(activities), inline=True)
                embed.set_image(url=user.banner)
                embed.set_footer(text=f"ID користувача: {member.id}")
            await inter.send(embed=embed)
        except Exception as e:
            if lang_server == 'ru':
                await inter.send(embed=disnake.Embed(
                    title="Что то пошло не так...",
                    description='Я не могу отобразить профиль данного пользователя \n'
                                'по следующим причинам: \n'
                                '- Указан не существующий пользователь \n\n'
                                '**Код ошибки (Для опытных пользователей):**\n'
                                f'```js\n{e}```\n'
                                ' `❓` Если это происходит не первый раз, обратитесь на [**сервер поддержки**](https://discord.gg/SpTBwz4xsa)',
                    color=0x2b2d31))
            if lang_server == 'en':
                await inter.send(embed=disnake.Embed(
                    title="Something went wrong...",
                    description="I can't display this user's profile\n"
                                "the following reasons: \n"
                                '- Non-existent user specified \n\n'
                                '**Error code (For advanced users):**\n'
                                f'```js\n{e}```\n'
                                ' `❓` If this is not the first time this has happened, please contact [**support server**](https://discord.gg/SpTBwz4xsa)',
                    color=0x2b2d31))
            if lang_server == 'uk':
                await inter.send(embed=disnake.Embed(
                    title="Щось пішло не так...",
                    description='Я не можу відобразити профіль користувача \n'
                                'з наступних причин: \n'
                                '- Вказано не існуючий користувач \n\n'
                                '**Код помилки (Для досвідчених користувачів):**\n'
                                f'```js\n{e}```\n'
                                ' `❓` Якщо це відбувається не вперше, зверніться на [**сервер підтримки**](https://discord.gg/SpTBwz4xsa)',
                    color=0x2b2d31))

    @commands.slash_command(description="🔧 Утилиты | Рандомное число")
    async def random(self, inter, ot: int = commands.Param(name="от", description="Введите число"), do: int = commands.Param(name="до", description="Введите число")):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        messages = {
            "ru": "Ваше число: {number}",
            "en": "Your number: {number}",
            "uk": "Ваше число: {number}"
        }

        try:
            message = messages.get(lang_server, messages["ru"])
            await inter.send(message.format(number=randint(ot, do)))
        except ValueError:
            message = messages.get(lang_server, messages["ru"])
            await inter.send(message.format(number=randint(do, ot)))

    @commands.slash_command(description="😀 Развлечения | Добавить репутацию пользователю")
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
    async def command_timely_error(self, inter, error):
        if isinstance(error, commands.CommandOnCooldown):
            lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
            if lang_server == 'ru':
                embed = disnake.Embed(description="Вы уже оценили пользователя, вы сможете сделать это снова через 24 часа!", color=0x2b2d31)
            if lang_server == 'uk':
                embed = disnake.Embed(description="Ви вже оцінили користувача, ви зможете зробити це знову за 24 години!", color=0x2b2d31)
            if lang_server == 'en':
                embed = disnake.Embed(description="You have already rated a user, you can do it again in 24 hours!", color=0x2b2d31)
            embed.set_author(name=f"{inter.author.name}", icon_url=f"{inter.author.avatar.url}")
            await inter.send(embed=embed)

    @commands.slash_command(name="8ball", description="😀 Развлечения | Спросить магичиский шар")
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
    async def language_error(self, inter):
        if isinstance(error, commands.MissingPermissions):
            lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
            if lang_server == 'ru':
                await inter.send("У вас должно быть право на управление сервером что бы установить язык", ephemeral=True)
            if lang_server == 'en':
                await inter.send("You must have the right to manage the server in order to set the language", ephemeral=True)
            if lang_server == 'uk':
                await inter.send("У вас має бути право на керування сервером щоб встановити мову", ephemeral=True)

def setup(bot):
    bot.add_cog(Main(bot))
