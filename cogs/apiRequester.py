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

import random
import aiohttp
import disnake
from db import SQLITE
from disnake.ext import commands
from googletrans import Translator

db = SQLITE("database.db")

async def translator(word, lang):
    return Translator().translate(word, dest=lang).text

class ApiRequester(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            lang = db.get(f"lang_{inter.guild.id}") or "ru"
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
                description=message[lang]['description'],
                color=0x2b2d31)
            await inter.edit_original_message(embed=embed)


    @commands.slash_command(description="😀 Выводит рандомную фотографию выбраного животного")
    async def animal(
            self, inter, 
            animal: str = commands.Param(
                name="животное", 
                description="Выберите животного", 
                choices={
                    'Лиса': 'fox', 
                    'Енот': 'raccoon', 
                    'Кошка': 'cat', 
                    'Собака':'dog',
                    'Птица': 'bird',
                    'Кенгуру': 'kangaroo',
                    'Коала': 'koala'
                }
            )
        ) -> None:
        await inter.response.defer()
        lang = db.get(f"lang_{inter.guild.id}") or "ru"
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
            embed = disnake.Embed(
                title=message[lang]['title'], 
                description=message[lang]['description'],
                color=0x2b2d31,
            )
            await inter.send(embed=embed)
    
    @commands.slash_command(
        description="😀 Развлечения | Выводит рандомную картинку для взрослых (поиск на rule34)"
    )
    async def nsfw(self, inter: disnake.ApplicationCommandInteraction, tags: str = commands.Param(name="поиск", description="Укажите тег для поиска, например: boy"), 
                   id: int = commands.Param(None, description="Укажите ID публикации (при неверном ID будет показана рандомная картинка)")
                  ):
        lang = db.get(f"lang_{inter.guild.id}") or "ru"
        if not inter.channel.is_nsfw():
            message = {
                'ru': 'Данную команду можно использовать только в NSFW каналах!',
                'en': 'This command can only be used in NSFW channels!',
                'uk': 'Цю команду можна використовувати лише у NSFW каналах!'
            }[lang]
            embed = disnake.Embed(description=message, color=0x2b2d31)
            return await inter.send(embed=embed, ephemeral=True)
        
        await inter.response.defer()
        embed = disnake.Embed(color=0x2b2d31)
        tags = await translator(tags, 'en')
        if not id:
            async with aiohttp.request("GET", f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&limit=1000&tags={tags}&json=1") as resp:
                data = await resp.json()
        else:
            async with aiohttp.request("GET", f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&id={id}&json=1") as resp:
                data = await resp.json()
        if not data:
            message = {
                'ru': 'Результаты не найдены, попробуйте поискать с помощью таких тегов как:\n `cum penis anal gay`',
                'en': 'No results found, try searching using tags such as:\n `cum penis anal gay`',
                'uk': 'Результати не знайдені, спробуйте пошукати за допомогою таких тегів як:\n `cum penis anal gay`'
            }[lang]
            return await inter.send(
                embed=disnake.Embed(
                    description=message, 
                    color=0x2b2d31
                ), 
                ephemeral=True
            )
        keyses = len(data) - 1
        rand = random.randint(0, keyses)
        embed.set_footer(text=f"ID: {data[rand]['id']}")
        embed.set_image(url=data[rand]['file_url'])
        await inter.send(embed=embed)

def setup(bot):
    bot.add_cog(ApiRequester(bot))

