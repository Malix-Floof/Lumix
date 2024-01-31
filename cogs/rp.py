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

import aiohttp
import disnake

from disnake.ext import commands
from db import SQLITE

db = SQLITE("database.db")


class RolePlay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'[ ОК ] Запущен rp.py')

    emote_list = ['Поцеловать', 'Обнять', 'Лизнуть', 'Устранить', 'Укусить', 'Прижаться', 'Ударить']

    @commands.slash_command(description=f"😜 RP | Взаимодействия с участниками")
    async def emote(
            self, inter,
            emote: str = commands.Param(
                name="эмоция",
                description="Выберите животного",
                choices=emote_list
            ),
            member: disnake.Member = commands.Param(
                name="пользователь",
                description="Выберите пользователя"
            ),
            text: str = commands.Param(
                None,
                name="текст",
                description="Напишите здесь что то"
            ),
    ):
        try:
            rp = f"> **{inter.author.name}:** *{text}*\n\n" if text else ""
            """ Kiss """
            if emote == 'Поцеловать':
                async with aiohttp.request("GET", "https://api.waifu.pics/sfw/kiss") as r:
                    request = await r.json()
                if member == inter.author:
                    await inter.send("Поцеловать самого себя, серьезно?", ephemeral=True)
                elif member.bot:
                    await inter.send("Вы не можете взаимодействовать с ботами!", ephemeral=True)
                else:
                    embed = disnake.Embed(
                        description=f"{rp}{inter.author.mention} **страстно целует** {member.mention}.\n"
                                    "У них любовь? ヽ(ﾟ〇ﾟ)ヽ", color=0x2b2d31)
                    embed.set_image(url=request['url'])
                    await inter.send(embed=embed)

            """ Lick """
            if emote == 'Лизнуть':
                async with aiohttp.request("GET", "https://api.waifu.pics/sfw/lick") as r:
                    request = await r.json()
                if member == inter.author:
                    await inter.send("Лизнуть самого себя, серьезно?", ephemeral=True)
                elif member.bot:
                    await inter.send("Вы не можете взаимодействовать с ботами!", ephemeral=True)
                else:
                    embed = disnake.Embed(
                        description=f"{rp}{inter.author.mention} **лизнул** {member.mention}.\n",
                        color=0x2b2d31)
                    embed.set_image(url=request['url'])
                    await inter.send(embed=embed)

            """ Hug """
            if emote == 'Обнять':
                async with aiohttp.request("GET", "https://api.waifu.pics/sfw/hug") as r:
                    request = await r.json()
                if member == inter.author:
                    await inter.send("Обнять самого себя, серьезно?", ephemeral=True)
                elif member.bot:
                    await inter.send("Вы не можете взаимодействовать с ботами!", ephemeral=True)
                else:
                    embed = disnake.Embed(
                        description=f"{rp}{inter.author.mention} **обнимает** {member.mention}.\nРазве это не мило? (･ω<)☆",
                        color=0x2b2d31
                    )
                    embed.set_image(url=request['url'])
                    await inter.response.send_message(embed=embed)

            """ Kill """
            if emote == 'Устранить':
                async with aiohttp.request("GET", "https://api.waifu.pics/sfw/kill") as r:
                    request = await r.json()
                if member == inter.author:
                    await inter.send("Устранить самого себя? Серьёзно?", ephemeral=True)
                if member.bot:
                    await inter.send("Вы не можете взаимодействовать с ботами!", ephemeral=True)
                else:
                    embed = disnake.Embed(
                        description=f"{rp}{inter.author.mention} **Устраняет** {member.mention}\nМинута молчания...",
                        color=0x2b2d31
                    )
                    embed.set_image(url=request['url'])
                    await inter.response.send_message(embed=embed)

            """ Bite """
            if emote == 'Укусить':
                async with aiohttp.request("GET", "https://api.waifu.pics/sfw/bite") as r:
                    request = await r.json()
                if member == inter.author:
                    await inter.send("Укусить самого себя, серьезно?", ephemeral=True)
                elif member.bot:
                    await inter.send("Вы не можете взаимодействовать с ботами!", ephemeral=True)
                else:
                    embed = disnake.Embed(
                        description=f"{rp}{inter.author.mention} **кусает** {member.mention}\nНаверное больно o(╥﹏╥)o",
                        color=0x2b2d31
                    )
                    embed.set_image(url=request['url'])
                    await inter.send(embed=embed)

            """ Cuddle """
            if emote == 'Прижаться':
                async with aiohttp.request("GET", "https://api.waifu.pics/sfw/cuddle") as r:
                    request = await r.json()
                if member == inter.author:
                    await inter.send("Прижаться к самому себе, серьезно?", ephemeral=True)
                if member.bot:
                    await inter.send("Вы не можете взаимодействовать с ботами!", ephemeral=True)
                else:
                    embed = disnake.Embed(
                        description=f"{rp}{inter.author.mention} **прижимается** {member.mention}.\nКак же это мило (✿◡‿◡)",
                        color=0x2b2d31
                    )
                    embed.set_image(url=request['url'])
                    await inter.send(embed=embed)

            """ Bonk """
            if emote == 'Ударить':
                async with aiohttp.request("GET", "https://api.waifu.pics/sfw/bonk") as r:
                    request = await r.json()
                if member == inter.author:
                    await inter.send("Ударить самого себя, серьезно?", ephemeral=True)
                if member.bot:
                    await inter.send("Вы не можете взаимодействовать с ботами!", ephemeral=True)
                else:
                    embed = disnake.Embed(
                        description=f"{rp}{inter.author.mention} **Ударил** {member.mention}.\nНо за что? ヽ(ﾟ〇ﾟ)ヽ",
                        color=0x2b2d31)
                    embed.set_image(url=request['url'])
                    await inter.send(embed=embed)

        except Exception as e:
            await inter.response.send_message(embed=disnake.Embed(
                title="Что то пошло не так...", 
                description=f"Я не могу данное действие \n"
                            "по следующим причинам: \n"
                            "- Данный Api сейчас не доступен \n\n"
                            "**Код ошибки (Для опытных пользователей):**\n"
                            f"```js\n{e}```"
                            "\n `❓` Если это происходит не первый раз,"
                            " обратитесь на [**сервер поддержки**](https://discord.gg/SpTBwz4xsa)",
                color=0x2b2d31
                ),
            )

    @commands.slash_command(description=f"😜 RP | Покраснеть")
    async def blush(self, inter):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        async with aiohttp.request("GET", "https://api.waifu.pics/sfw/blush") as r:
            request = await r.json()
        if lang_server == 'ru':
            embed = disnake.Embed(description=f"{inter.author.mention} **покраснел**\nНаверное, стало стыдно ┌༼ ⊘ _ ⊘ ༽┐", color=0x2b2d31)
        if lang_server == 'en':
            embed = disnake.Embed(description=f"{inter.author.mention} **blushed**\nProbably felt ashamed ┌༼ ⊘ _ ⊘ ༽┐", color=0x2b2d31)
        if lang_server == 'uk':
            embed = disnake.Embed(description=f"{inter.author.mention} **покраснел**\nНаверное, стало стидно ┌༼ ⊘ _ ⊘ ༽┐", color=0x2b2d31)
        embed.set_image(url=request['url'])
        await inter.send(embed=embed)

    @commands.slash_command(description=f"😜 RP | Заплакать")
    async def cry(self, inter):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        async with aiohttp.request("GET", "https://api.waifu.pics/sfw/cry") as r:
            request = await r.json()
        if lang_server == 'ru':
            embed = disnake.Embed(description=f"{inter.author.mention} **плачет**\nПожалейте кто нибудь (●´ω｀●)", color=0x2b2d31)
        if lang_server == 'en':
            embed = disnake.Embed(description=f"{inter.author.mention} **cries**\nPity someone (●´ω｀●)", color=0x2b2d31)
        if lang_server == 'uk':
            embed = disnake.Embed(description=f"{inter.author.mention} **плачет**\nПожаліте хто нибудь (●´ω｀●)", color=0x2b2d31)
        embed.set_image(url=request['url'])
        await inter.send(embed=embed)

    @commands.slash_command(description=f"😜 RP | Танцевать")
    async def dance(self, inter):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        async with aiohttp.request("GET", "https://api.waifu.pics/sfw/dance") as r:
            request = await r.json()
        if lang_server == 'ru':
            embed = disnake.Embed(description=f"{inter.author.mention} **танцует**\nПравда круто? ໒( • ͜ʖ • )७", color=0x2b2d31)
        if lang_server == 'en':
            embed = disnake.Embed(description=f"{inter.author.mention} **dancing**\nReally cool? ໒( • ͜ʖ • )७", color=0x2b2d31)
        if lang_server == 'uk':
            embed = disnake.Embed(description=f"{inter.author.mention} **танцює**\nПравда круто? ໒( • ͜ʖ • )७", color=0x2b2d31)
        embed.set_image(url=request['url'])
        await inter.send(embed=embed)

    @commands.slash_command(description=f"😜 RP | Радоваться")
    async def happy(self, inter):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        async with aiohttp.request("GET", "https://api.waifu.pics/sfw/happy") as r:
            request = await r.json()
        if lang_server == 'ru':
            embed = disnake.Embed(description=f"{inter.author.mention} **радуется**\nЧто же произошло? (⊙ω⊙)", color=0x2b2d31)
        if lang_server == 'en':
            embed = disnake.Embed(description=f"{inter.author.mention} **rejoices**\nWhat happened? (⊙ω⊙)", color=0x2b2d31)
        if lang_server == 'uk':
            embed = disnake.Embed(description=f"{inter.author.mention} **радіє**\nЩо ж сталося? (⊙ω⊙)", color=0x2b2d31)
        embed.set_image(url=request['url'])
        await inter.send(embed=embed)


def setup(bot):
    bot.add_cog(RolePlay(bot))
