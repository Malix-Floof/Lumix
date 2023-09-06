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
        if lang_server == 'ru':
            nfakt = "Факт:"
        if lang_server == 'en':
            nfakt = "Fact:"
        if lang_server == 'uk':
            nfakt = "Факт:"
        try:
            if animal == 'Лиса':
                async with aiohttp.request("GET", "https://some-random-api.com/animal/fox") as resp:
                    data = await resp.json()
                word = data['fact']
                fact = await translator(word, lang_server)
                embed = disnake.Embed(description=f"**{nfakt}** {fact}", color=0x2b2d31)
                embed.set_image(url=data['image'])
                await inter.send(embed=embed)
            elif animal == 'Енот':
                async with aiohttp.request("GET", "https://some-random-api.com/animal/raccoon") as resp:
                    data = await resp.json()
                word = data['fact']
                fact = await translator(word, lang_server)
                embed = disnake.Embed(description=f"**{nfakt}** {fact}", color=0x2b2d31)
                embed.set_image(url=data['image'])
                await inter.send(embed=embed)
            elif animal == 'Кошка':
                async with aiohttp.request("GET", "https://some-random-api.com/animal/cat") as resp:
                    data = await resp.json()
                word = data['fact']
                fact = await translator(word, lang_server)
                embed = disnake.Embed(description=f"**{nfakt}** {fact}", color=0x2b2d31)
                embed.set_image(url=data['image'])
                await inter.send(embed=embed)
            elif animal == 'Собака':
                async with aiohttp.request("GET", "https://some-random-api.com/animal/dog") as resp:
                    data = await resp.json()
                word = data['fact']
                fact = await translator(word, lang_server)
                embed = disnake.Embed(description=f"**{nfakt}** {fact}", color=0x2b2d31)
                embed.set_image(url=data['image'])
                await inter.send(embed=embed)
            elif animal == 'Птица':
                async with aiohttp.request("GET", "https://some-random-api.com/animal/bird") as resp:
                    data = await resp.json()
                word = data['fact']
                fact = await translator(word, lang_server)
                embed = disnake.Embed(description=f"**{nfakt}** {fact}", color=0x2b2d31)
                embed.set_image(url=data['image'])
                await inter.send(embed=embed)
            elif animal == 'Кенгуру':
                async with aiohttp.request("GET", "https://some-random-api.com/animal/kangaroo") as resp:
                    data = await resp.json()
                word = data['fact']
                fact = await translator(word, lang_server)
                embed = disnake.Embed(description=f"**{nfakt}** {fact}", color=0x2b2d31)
                embed.set_image(url=data['image'])
                await inter.send(embed=embed)
            elif animal == 'Коала':
                async with aiohttp.request("GET", "https://some-random-api.com/animal/koala") as resp:
                    data = await resp.json()
                word = data['fact']
                fact = await translator(word, lang_server)
                embed = disnake.Embed(description=f"**{nfakt}** {fact}", color=0x2b2d31)
                embed.set_image(url=data['image'])
                await inter.send(embed=embed)
        except Exception as e:
            if lang_server == 'ru':
                await inter.send(embed=disnake.Embed(title="Что то пошло не так...", description=f"Я не могу данное действие \nпо следующим причинам: \n- Данный Api сейчас не доступен \n\n**Код ошибки (Для опытных пользователей):**\n```js\n{e}```\n `❓` Если это происходит не первый раз, обратитесь на [**сервер поддержки**](https://discord.gg/SpTBwz4xsa)", color=0x2b2d31))
            if lang_server == 'en':
                await inter.send(embed=disnake.Embed(title="Something went wrong...", description=f"I can't do this \nfor the following reasons: \n- This Api is currently not available \n\n**Error code (for advanced users):**\n```js\n{e}```\n `❓` If this is not the first time this happens, contact the [**support server**](https://discord.gg/SpTBwz4xsa)", color=0x2b2d31))
            if lang_server == 'uk':
                await inter.send(embed=disnake.Embed(title="Щось пішло не так...", description=f"Я не можу цю дію \nз наступних причин: \n- Даний Api зараз не доступний \n\n**Код помилки (Для досвідчених користувачів):**\n```js\n{e}```\n `❓` Якщо це відбувається не вперше, зверніться на [**сервер підтримки**](https://discord.gg/SpTBwz4xsa)", color=0x2b2d31))


def setup(bot):
    bot.add_cog(ApiRequester(bot))
