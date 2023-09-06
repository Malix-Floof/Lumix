import disnake
from disnake.ext import commands
import aiohttp
from db import SQLITE
from googletrans import Translator

db = SQLITE("database.db")
filters = ['Сепия', 'Радуга', 'Стекло', 'Пиксели', 'Холод', 'Монохром', 'Светлый']
animal_list = ['Лиса', 'Кошка', 'Собака', 'Птица', 'Коала', 'Кенгуру', 'Енот']

async def translator(word, lang_server):
        translator = Translator()
        result = translator.translate(word, dest = lang_server)
        return result.text

class ApiRequester(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False


    @commands.slash_command(description="🔧 Утилиты | Изменить стиль аватарки")
    async def filter(self, inter, filter: str = commands.Param(name="фильтр", description="Выберите фильтр", choices=filters),
        member: disnake.Member = commands.Param(name="пользователь", description="Выберите пользователя")):
        try:
            await inter.response.defer()
            lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
            if lang_server == "ru":
                embed = disnake.Embed(title="Результат:", color=0x2b2d31)
                embed.set_author(name=f'Запросил: {inter.author.name}', icon_url=inter.author.display_avatar)
            if lang_server == 'en':
                embed = disnake.Embed(title="Result:", color=0x2b2d31)
                embed.set_author(name=f'Requested: {inter.author.name}', icon_url=inter.author.display_avatar)
            if lang_server == 'uk':
                embed = disnake.Embed(title="Результат:", color=0x2b2d31)
                embed.set_author(name=f'Запитав: {inter.author.name}', icon_url=inter.author.display_avatar)
            if filter == 'Радуга':
                resp = f"https://some-random-api.com/canvas/gay?avatar={member.display_avatar.url}"
                embed.set_image(url=resp)
                await inter.send(embed=embed)
            elif filter == 'Сепия':
                resp = f"https://some-random-api.com/canvas/sepia?avatar={member.display_avatar.url}"
                embed.set_image(url=resp)
                await inter.send(embed=embed)
            elif filter == 'Стекло':
                resp = f"https://some-random-api.com/canvas/glass?avatar={member.display_avatar.url}"
                embed.set_image(url=resp)
                await inter.send(embed=embed)
            elif filter == 'Пиксели':
                resp = f"https://some-random-api.com/canvas/misc/pixelate?avatar={member.display_avatar.url}"
                embed.set_image(url=resp)
                await inter.send(embed=embed)
            elif filter == 'Холод':
                resp = f"https://some-random-api.com/canvas/blurple?avatar={member.display_avatar.url}"
                embed.set_image(url=resp)
                await inter.send(embed=embed)
            elif filter == 'Монохром':
                resp = f"https://some-random-api.com/canvas/threshold?avatar={member.display_avatar.url}"
                embed.set_image(url=resp)
                await inter.send(embed=embed)
            elif filter == 'Светлый':
                resp = f"https://some-random-api.com/canvas/brightness?avatar={member.display_avatar.url}"
                embed.set_image(url=resp)
                await inter.send(embed=embed)
        except Exception as e:
            if lang_server == 'ru':
                await inter.edit_original_message(embed=disnake.Embed(title="Что-то пошло не так...",
                                                description=f"Я не могу выполнить данное действие по следующим причинам:\n- Данный API сейчас недоступен\n\n**Код ошибки (для опытных пользователей):**\n```js\n{e}```\n❓ Если это происходит не в первый раз, обратитесь на [**сервер поддержки**](https://discord.gg/SpTBwz4xsa)",
                                                color=0x2b2d31))
            if lang_server == 'en':
                await inter.edit_original_message(embed=disnake.Embed(title="Something went wrong...",
                                                description=f"I can't perform this action for the following reasons:\n- This API is currently unavailable\n\n**Error code (for advanced users):**\n```js\n{e}```\n❓ If this is not the first time this has happened, please contact [**support server**](https://discord.gg/SpTBwz4xsa)",
                                                color=0x2b2d31))
            if lang_server == 'uk':
                await inter.edit_original_message(embed=disnake.Embed(title="Щось пішло не так...",
                                                description=f"Я не можу виконати цю дію з наступних причин:\n- Даний API зараз недоступний\n\n**Код помилки (для досвідчених користувачів):**\n```js\n{e}```\n❓ Якщо це не вперше, зверніться на [**сервер підтримки**](https://discord.gg/SpTBwz4xsa)",
                                                color=0x2b2d31))


    @commands.slash_command(description=f"😀 Развлечения | Выводит рандомную фотографию выбраного животного")
    async def animal(self, inter, animal: str = commands.Param(name="животное", description="Выберите животного", choices=animal_list)):
        await inter.response.defer()
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        messages = {
            'ru': 'Факт:',
            'en': 'Fact:',
            'uk': 'Факт:',
        }
        nfakt = messages[lang_server]
        animals = {
            'Лиса': "https://some-random-api.com/animal/fox",
            'Енот': "https://some-random-api.com/animal/raccoon",
            'Кошка': "https://some-random-api.com/animal/cat",
            'Собака': "https://some-random-api.com/animal/dog",
            'Птица': "https://some-random-api.com/animal/bird",
            'Кенгуру': "https://some-random-api.com/animal/kangaroo",
            'Коала': "https://some-random-api.com/animal/koala"
        }
        async with aiohttp.request("GET", animals[animal]) as resp:
            if resp.status != 200:
                return await inter.send("Api сейчас не доступен", ephemeral=True)
            else:
                data = await resp.json()
        word = data['fact']
        fact = await translator(word, lang_server)
        embed = disnake.Embed(description=f"**{nfakt}** {fact}", color=0x2b2d31)
        embed.set_image(url=data['image'])
        await inter.send(embed=embed)

def setup(bot):
    bot.add_cog(ApiRequester(bot))
