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
        print(f"utils.py is ready")


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
            'Русский': 'ru',
            'Украинский': 'uk'
        }

        if lang in lang_map:
            tts = gTTS(text=text, lang=lang_map[lang])
            tts.save(f"./cores/gtts/{lang_map[lang]}-voice.mp3")
        if lang_server == 'ru':
            await inter.send("Результат:", file=disnake.File(f"./cores/gtts/{lang_map[lang]}-voice.mp3"))
        if lang_server == 'en':
            await inter.send("Result:", file=disnake.File(f"./cores/gtts/{lang_map[lang]}-voice.mp3"))
        if lang_server == 'uk':
            await inter.send("Результат:", file=disnake.File(f"./cores/gtts/{lang_map[lang]}-voice.mp3"))

    @gtts.error
    async def gtts_error(self, inter):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        if lang_server == 'ru':
            embed = disnake.Embed(description=f"Простите, данный язык сейчас не доступен!", color=0x2b2d31)
        if lang_server == 'en':
            embed = disnake.Embed(description=f"Sorry, this language is currently not available!", color=0x2b2d31)
        if lang_server == 'uk':
            embed = disnake.Embed(description=f"Вибачте, ця мова зараз не доступна!", color=0x2b2d31)
        embed.set_author(name=f"{inter.author.name}", icon_url=f"{inter.author.avatar.url}")
        await inter.send(embed=embed)


    @commands.slash_command(description=f"🔧 Утилиты | Показывает аватарку пользователя")
    async def avatar(self, inter, user: disnake.Member = commands.Param(name="пользователь", description="Выберите пользователя")):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        member = user or inter.user
        if user is None:
            formats = [
                f"PNG({user.display_avatar.replace(format='png', size=1024).url}) | ",
                f"JPG({user.display_avatar.replace(format='jpg', size=1024).url})",
                f" | WebP({user.display_avatar.replace(format='WebP', size=1024).url})",
                f" | GIF({user.display_avatar.replace(format='gif', size=1024).url})" if user.display_avatar.is_animated() else ""
            ]
            if lang_server == 'ru':
                embed = disnake.Embed(title="Твоя аватарка", description=' '.join(formats), color=0x2b2d31)
            if lang_server == 'en':
                embed = disnake.Embed(title="You avatar", description=' '.join(formats), color=0x2b2d31)
            if lang_server == 'uk':
                embed = disnake.Embed(title="Твоя аватарка", description=' '.join(formats), color=0x2b2d31)
            embed.set_image(url=inter.author_avatar.url)
            await inter.send(embed=embed)
        else:
            formats = [
                f"[PNG]({user.display_avatar.replace(format='png', size=1024).url}) | ",
                f"[JPG]({user.display_avatar.replace(format='jpg', size=1024).url})",
                f" | [WebP]({user.display_avatar.replace(format='webp', size=1024).url})",
                f" | [GIF]({user.display_avatar.replace(format='gif', size=1024).url})" if user.display_avatar.is_animated() else ""
            ]
            if lang_server == 'ru':
                embed = disnake.Embed(title=f"Аватарка {'бота' if user.bot else 'пользователя'} {member.name}", description=' '.join(formats), color=0x2b2d31)
            if lang_server == 'en':
                embed = disnake.Embed(title=f"{'Bot' if user.bot else 'User'} avatar {member.name}", description=' '.join(formats), color=0x2b2d31)
            if lang_server == 'uk':
                embed = disnake.Embed(title=f"Аватарка {'бота' if user.bot else 'користувача'} {member.name}", description=' '.join(formats), color=0x2b2d31)
            embed.set_image(url=member.display_avatar.url)
            await inter.send(embed=embed)

    @commands.slash_command(description="🔧 Утилиты | Автороли")
    @commands.has_permissions(administrator=True)
    async def autorole(self, inter, role: disnake.Role):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        if role.name == "@everyone":
            db.delete(f"autorole_{inter.guild.id}")
            if lang_server == 'ru':
                embed = disnake.Embed(description="**Автороль была убрана для сервера**", color=0x2b2d31)
            elif lang_server == 'en':
                embed = disnake.Embed(description="**Author role has been removed for the server**", color=0x2b2d31)
            elif lang_server == 'uk':
                embed = disnake.Embed(description="**Автороль була прибрана для сервера**", color=0x2b2d31)
        else:
            db.set(f"autorole_{inter.guild.id}", str(role.id))
            if lang_server == 'ru':
                embed = disnake.Embed(description=f"**Когда кто-то присоединяется к серверу, роль <@&{role.id}> будет автоматически выдана пользователю**", color=0x2b2d31)
            elif lang_server == 'en':
                embed = disnake.Embed(description=f"**When someone joins the server, the <@&{role.id}> role will automatically be assigned to the user**", color=0x2b2d31)
            elif lang_server == 'uk':
                embed = disnake.Embed(description=f"**Коли хтось приєднується до сервера, роль <@&{role.id}> буде автоматично видана користувачу**", color=0x2b2d31)
        await inter.send(embed=embed)

    @autorole.error
    async def autorole_error(self, inter, error):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        if isinstance(error, commands.MissingPermissions):
            if lang_server == 'ru':
                await inter.send("У вас должно быть право администратора что бы установить автоматическую выдачу ролей", ephemeral=True)
            if lang_server == 'en':
                await inter.send("You must have administrator rights to set the automatic distribution of roles", ephemeral=True)
            if lang_server == 'uk':
                await inter.send("У вас має бути право адміністратора щоб встановити автоматичну видачу ролей", ephemeral=True)

def setup(bot):
    bot.add_cog(CogUtils(bot))
