import disnake
from disnake.ext import commands
import aiohttp
from db import SQLITE
from googletrans import Translator

db = SQLITE("database.db")
animal_list = ['Лиса', 'Кошка', 'Собака', 'Птица', 'Коала', 'Кенгуру', 'Енот']

async def translator(word, lang_server):
    translator = Translator()
    result = translator.translate(word, dest = lang_server)
    return result.text

class ApiRequester(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False

    @commands.Cog.listener()
    async def on_ready(self):
        await db.initialize()

    API_URL = 'https://some-random-api.com/canvas/'
    CHOICES = {
        'Сепия': ['sepia?avatar={0}'], 
        'Радуга': ['gay?avatar={0}'], 
        'Стекло': ['glass?avatar={0}'], 
        'Пиксели': ['pixelate?avatar={0}'], 
        'Холод': ['blurple?avatar={0}'], 
        'Монохром': ['threshold?avatar={0}'], 
        'Светлый': ['brightness?avatar={0}']
    }

    @commands.slash_command(description="🔧 Утилиты | Изменить стиль аватарки")
    async def filter(
            self, inter, 
            filter: str = commands.Param(
                name="фильтр", 
                description="Выберите фильтр", 
                choices=list(CHOICES.keys()
                )
            ),
        member: disnake.Member = commands.Param(
            name="пользователь", 
            description="Выберите пользователя"
            )
        ):
        try:
            await inter.response.defer()
            lang = await db.get(f"lang_{inter.guild.id}") or "ru"
            message = {
                'ru': 'Результат:',
                'en': 'Result:',
                'uk': 'Результат:'
            }[lang]
            embed = disnake.Embed(title=message, color=0x2b2d31)
            data = self.CHOICES[filter][0].format(member.display_avatar.url)
            resp = self.API_URL + data
            embed.set_image(url=resp)
            await inter.send(embed=embed)
        except Exception as e:
            message = {
                'ru': {
                    'title': 'Что-то пошло не так...',
                    'description': 'Возникла проблема при отправке запроса на сервер'
                },
                'en': {
                    'title': 'Something went wrong...',
                    'description': 'There was a problem when sending a request to the server'
                },
                'uk': {
                    'title': 'Щось пішло не так...',
                    'description': ''
                }
            }
            embed = disnake.Embed(
                title=message[lang]['title'],
                description=message[lang]['description'])
            await inter.edit_original_message(embed=embed, color=0x2b2d31)


    @commands.slash_command(description="😀 Развлечения | Выводит рандомную фотографию выбраного животного")
    async def animal(
            self, inter, 
            animal: str = commands.Param(
                name="животное", 
                description="Выберите животного", 
                choices={'Лиса': 'fox', 
                         'Енот': 'raccoon', 
                         'Кошка': 'cat', 
                         'Собака':'dog',
                         'Птица': 'bird',
                         'Кенгуру': 'kangaroo',
                         'Коала': 'koala'}
            )
        ):
        await inter.response.defer()
        lang = await db.get(f"lang_{inter.guild.id}") or "ru"
        nfakt = {
            'ru': 'Факт:',
            'en': 'Fact:',
            'uk': 'Факт:'
        }[lang]
        try:
            async with aiohttp.request("GET", f"https://some-random-api.com/animal/{animal}") as resp:
                data = await resp.json()
            word = data['fact']
            fact = await translator(word, lang)
            embed = disnake.Embed(description=f"**{nfakt}** {fact}", color=0x2b2d31)
            embed.set_image(url=data['image'])
            await inter.send(embed=embed)
        except Exception as e:
            message = {
                'ru': {
                    'title': 'Что-то пошло не так...',
                    'description': 'Возникла проблема при отправке запроса на сервер'
                },
                'en': {
                    'title': 'Something went wrong...',
                    'description': 'There was a problem when sending a request to the server'
                },
                'uk': {
                    'title': 'Щось пішло не так...',
                    'description': 'Виникла проблема під час надсилання запиту на сервер'
                }
            }
            embed = disnake.Embed(title=message[lang]['title'], description=message[lang]['description'])
            await inter.send(embed=embed, color=0x2b2d31)


def setup(bot):
    bot.add_cog(ApiRequester(bot))
