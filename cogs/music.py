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

import mafic
import asyncio
import json
import time
import disnake

from disnake.ext import commands, components
from random import shuffle
from config import emojis
from db import SQLITE
from typing import List

db = SQLITE("database.db")
posEmoji = "<:5_:1083430173900292178>"
leftEmoji = "<:3_:1083430185761783878>"


class DJSettings(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.user_select(placeholder="Участники...", custom_id="membersdj:0")
    async def settings(self, select, inter):
        await inter.response.defer()


class MusicButtons(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.select(
        placeholder="Настройки...", 
        options=[disnake.SelectOption(label="Установить диджея", value="dj")],
        custom_id="select:0"
    )
    async def settings(self, select, inter):
        await inter.response.defer()

    @disnake.ui.button(emoji=emojis['backEmoji'], custom_id="back:1")
    async def back(self, button, inter):
        await inter.response.defer()

    @disnake.ui.button(emoji=emojis['pauseEmoji'], custom_id="pause:2")
    async def pause(self, button, inter):
        await inter.response.defer()

    @disnake.ui.button(emoji=emojis['skipEmoji'], custom_id="skip:3")
    async def skip(self, button, inter):
        await inter.response.defer()

    @disnake.ui.button(emoji=emojis['playlistEmoji'], custom_id="playlist:4")
    async def playlist(self, button, inter):
        ...
        
    @disnake.ui.button(emoji=emojis['volumepEmoji'], custom_id="volumep:5")
    async def volumep(self, button, inter):
        await inter.response.defer()

    @disnake.ui.button(emoji=emojis['shuffleEmoji'], custom_id="qsuffle:6")
    async def qshuffle(self, button, inter):
        ...

    @disnake.ui.button(emoji=emojis['stopEmoji'], custom_id="stop:7")
    async def stop(self, button, inter):
        await inter.response.defer()

    @disnake.ui.button(emoji=emojis['loopEmoji'], custom_id="loop:8")
    async def loop(self, button, inter):
        await inter.response.defer()

    @disnake.ui.button(emoji=emojis['bassboostEmoji'], custom_id="bassboost:9")
    async def bassboost(self, button, inter):
        await inter.response.defer()

    @disnake.ui.button(emoji=emojis['volumemEmoji'], custom_id="volumem:10")
    async def volumem(self, button, inter):
        await inter.response.defer()

class Player(mafic.Player):
    __slots__ = (
        "queue"
        "djs",
        "controller",
        "max_size",
        "pages",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue: List[mafic.Track] = []
        self.djs: List[disnake.Member] = []
        self.pages: List[disnake.Embed] = []
        self.controller: disnake.Message = None
        self.controller_id: int = 0 
        self.is_looping: bool = False
        self.loop_mode: str = None
        self.volume: int = 100
        self.index: int = 0

    async def queue_type(self, value):
        self.loop_mode = value
        self.is_looping = value in ('track', 'queue')

class Music(commands.Cog):
    __slots__ = (
        "oh",
        "effect",
    )
    def __init__(self, bot):
        self.bot = bot
        self.oh: dict[str] = {}
        self.effect: dict[bool] = {}


    async def make_buttons(self, page: int, pages: int):
        queues = pages == 1
        button_data = [
            ("◀️", "prev", disnake.ButtonStyle.blurple, queues),
            ("Перейти к странице", "stop", disnake.ButtonStyle.gray, queues),
            ("▶️", "next", disnake.ButtonStyle.blurple, queues)
        ]
        buttons = [
            disnake.ui.Button(
                label=label,
                custom_id=await self.hey_listen.build_custom_id(page=page, where=where, pages=pages),
                style=style,
                disabled=disabled
            )
            for label, where, style, disabled in button_data
        ]
        return buttons

    async def destroy(self, player: Player):
        if not player.queue:
            await player.controller.edit(view=None)
            return await player.destroy()

        if player.loop_mode == 'track':
            return await player.play(player.queue[0])

        if player.loop_mode == 'queue':
            player.index = (player.index + 1) % len(player.queue)
            return await player.play(player.queue[player.index])

        player.queue.pop(0)
        if player.queue:
            return await player.play(player.queue[0])
    
        await player.controller.edit(view=None)
        await player.destroy()

    @commands.Cog.listener("on_track_exception")
    @commands.Cog.listener("on_track_end")
    @commands.Cog.listener("on_track_stuck")
    async def сonditions(self, event):
        await self.destroy(event.player)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        player = member.guild.voice_client
        if not player:
            return

        elif not any(not member.bot for member in player.channel.members):
            await self.destroy(player)
            return

        elif member.id == self.bot.user.id and after.channel is None:
            await self.destroy(player)
            return

        elif before.channel is not None and after.channel is None:
            if member.id in player.djs:
                player.djs.pop(member.id)

    async def cheks(self, inter, player):
        if not inter.user.voice:
            await inter.followup.send(
                f"{inter.author.mention} Вы должны находиться в голосовом канале с ботом что бы управлять музыкой!", 
                delete_after=5,
            )
            return False

        if player.djs:
            if not inter.author.id in player.djs:
                await inter.followup.send(f"{inter.author.mention} Вы не являетесь диджеем!", delete_after=5)
                return False

        return True

    async def volume_blocked(self, player):
        view = MusicButtons()
        volume = player.volume
        if volume <= 0:
            view.children[10].disabled = True
            view.children[10].style = disnake.ButtonStyle.red
        elif volume >= 200:
            view.children[5].disabled = True
            view.children[5].style = disnake.ButtonStyle.red
        else:
            view.children[5].disabled = False
            view.children[5].style = disnake.ButtonStyle.grey
            view.children[10].disabled = False
            view.children[10].style = disnake.ButtonStyle.grey

        await player.controller.edit(view=view)

    @commands.Cog.listener("on_dropdown")
    @commands.Cog.listener("on_button_click")
    @commands.Cog.listener("on_modal_submit")
    async def interaction(self, inter):
        i = inter.guild.id
        lang = db.get(f"lang_{i}") or "ru"
        player = inter.guild.voice_client
        track = player.current
        view = MusicButtons()
        if inter.data['custom_id'] == 'membersdj:0':
            for dj in inter.data.values:
                member = inter.guild.get_member(int(dj))
                if member.bot:
                    return await inter.followup.send("Бот не может быть диджеем!", delete_after=5)

                if not member in inter.guild.voice_client.channel.members:
                    return await inter.followup.send("Данного участника нет в голосовом канале!", delete_after=5)

                if dj in player.djs:
                    player.djs.pop(dj)
                    await inter.followup.send(f"<@{inter.data.values[0]}> Был убран из списка диджеев!", delete_after=5)
                else:
                    player.djs.append(dj)
                    await inter.followup.send(f"<@{inter.data.values[0]}> Был добавлен в список диджеев!", delete_after=5)

        if inter.data['custom_id'] == 'select:0':
            await self.cheks(inter, player)

            if inter.data['values'][0] == 'dj':
                embed = disnake.Embed(
                    title="Настройка диджея канала",
                    description="Укажите участника который будет управлять музыкальным плеером в канале, он сможет останавливать, пропускать, а так же изменять фильтры треков",
                    color=0x2b2d31
                )
            await inter.followup.send(embed=embed, ephemeral=True, view=DJSettings())

        if inter.data['custom_id'] == 'back:1':
            if await self.cheks(inter, player):
                await player.seek(0)
                await player.controller.edit(view=view)

        if inter.data['custom_id'] == 'pause:2':
            if await self.cheks(inter, player):
                buttons = [1, 3, 4, 5, 6, 7, 8, 9, 10]
                dbuttons = False if player.paused else True
                emoji = emojis['pauseEmoji'] if player.paused else emojis['playEmoji']
                style = disnake.ButtonStyle.gray if player.paused else disnake.ButtonStyle.blurple

                for button in buttons:
                    view.children[button].disabled = dbuttons
                    view.children[2].emoji = emoji
                    view.children[2].style = style

                if player.is_looping:
                    view.children[8].emoji = emojis['onLoopMode']
                    view.children[8].style = disnake.ButtonStyle.blurple

                if self.effect[inter.guild.id] is True:
                    view.children[9].style = disnake.ButtonStyle.red

                if player.paused:
                    await player.resume()
                    await self.update_embed(player)
                else:
                    await player.pause()

                await player.controller.edit(view=view)

        if inter.data['custom_id'] == 'skip:3':
            if await self.cheks(inter, player):
                message = {
                    'ru': f'{inter.author.name} пропустил(-а) трек {track.title}',
                    'en': f'{inter.author.name} missed a track {track.title}',
                    'uk': f'{inter.author.name} пропустив(-ла) трек {track.title}'
                }[lang]
                await player.stop()
                await inter.followup.send(message, delete_after=5)

        if inter.data['custom_id'] == 'playlist:4':
            durations = sum([track.length / 1000 for track in player.queue])
            hours, remainder = divmod(durations, 3600)
            qsize = len(player.queue)
            description = None
            tracks = [
                f"{'### ' if i == 0 else ''}{i + 1}. `{time.strftime('%M:%S', time.gmtime(track.length / 1000))}` - [{(track.title[:25] + '...') if len(track.title) > 25 else track.title}]({track.uri}) {'🎶' if i == 0 else ''}" 
                for i, track in enumerate(player.queue)
            ]
            if hours == 0:
                durations = {
                    'ru': f'`{int(time.strftime("%M", time.gmtime(remainder)))} мин.`',
                    'en': f'`{int(time.strftime("%M", time.gmtime(remainder)))} min.`',
                    'uk': f'`{int(time.strftime("%M", time.gmtime(remainder)))} хв.`'
                }[lang]
                description = {
                    'ru': f'{qsize} трек(-ов), примерное время {durations}',
                    'en': f'{qsize} track(s), estimated time {durations}',
                    'uk': f'{qsize} трек(-ів), зразковий час {durations}'
                }[lang]
            else:
                durations = {
                    'ru': f'`{int(hours)} ч. {int(time.strftime("%M", time.gmtime(remainder)))} мин.`',
                    'en': f'`{int(hours)} h. {int(time.strftime("%M", time.gmtime(remainder)))} min.`',
                    'uk': f'`{int(hours)} год. {int(time.strftime("%M", time.gmtime(remainder)))} хв.`'
                }[lang]
                description = {
                    'ru': f'{qsize} трек(-ов), примерное время {durations}',
                    'en': f'{qsize} track(s), estimated time {durations}',
                    'uk': f'{qsize} трек(-ів), зразковий час {durations}'
                }[lang]
            player.pages.clear()
            ppp = {
                'ru': 'Страница',
                'en': 'Page',
                'uk': 'Сторінка'
            }[lang]

            for b in range(0, len(tracks), 10):
                page_tracks = tracks[b:b+10]
                text = "\n".join(page_tracks)
                embed = disnake.Embed(
                    title="Очередь сервера",
                    description=f"{description}\n\n{text}",
                    color=0x2b2d31
                )
                embed.set_footer(
                    text=f"{ppp} {len(player.pages) + 1} / {len([tracks[i:i + 10] for track in range(0, len(tracks), 10)])}",
                    icon_url=inter.user.avatar
                )
                player.pages.append(embed)

            await inter.send(embed=player.pages[0], ephemeral=True, components=await self.make_buttons(0, len(player.pages)))

        if inter.data['custom_id'] == 'volumep:5':
            if await self.cheks(inter, player):
                player.volume += 10
                await player.set_volume(player.volume)
                await self.volume_blocked(player)
                if player.is_looping:
                    view.children[8].emoji = emojis['onLoopMode']
                    view.children[8].style = disnake.ButtonStyle.blurple
                if self.effect[inter.guild.id]:
                    view.children[9].style = disnake.ButtonStyle.red
                await player.controller.edit(embed=await self.playerMessage(player))

        if inter.data['custom_id'] == 'qsuffle:6':
            if await self.cheks(inter, player):
                if len(player.queue) < 3:
                    message = {
                        'ru': 'Мало треков в очереди! Требуется как минимум 3',
                        'en': 'Few tracks in the queue! Requires at least 3',
                        'uk': 'Мало треків у черзі! Потрібно як мінімум 3'
                    }[lang]
                    await inter.send(message, ephemeral=True)
                    return

                shuffle(player.queue)
                message = {
                    'ru': 'Очередь была перемешана',
                    'en': 'The queue has been jumbled',
                    'uk': 'Черга була перемішана'
                }[lang]
                await inter.send(message, ephemeral=True)

        if inter.data['custom_id'] == 'stop:7':
            if await self.cheks(inter, player):
                await self.destroy(player)

        if inter.data['custom_id'] == 'loop:8':
            if await self.cheks(inter, player):
                loopMode = player.loop_mode
                if loopMode is None or loopMode == "queue":
                    loopMode = 'track' if loopMode == "queue" else 'queue'
                    emoji = '🔂' if loopMode == 'track' else '🔁'
                    style = disnake.ButtonStyle.blurple if loopMode in ['queue', 'track'] else disnake.ButtonStyle.gray
                else:
                    loopMode = None
                    emoji = '🔁'
                    style = disnake.ButtonStyle.gray

                await player.queue_type(loopMode)

                view.children[8].emoji = emoji
                view.children[8].style = style
                if self.effect[inter.guild.id]:
                    view.children[9].style = disnake.ButtonStyle.red

                return await player.controller.edit(view=view)


        if inter.data['custom_id'] == 'bassboost:9':
            if await self.cheks(inter, player):
                if self.effect[i] is False:
                    view.children[9].style = disnake.ButtonStyle.red
                    self.effect[i] = True
                    await player.add_filter(mafic.Filter(karaoke=mafic.Karaoke(3, 3)), label="karaoke", fast_apply=True)
                    if player.is_looping:
                        view.children[8].emoji = emojis['onLoopMode']
                        view.children[8].style = disnake.ButtonStyle.blurple
                    await player.controller.edit(view=view)
                    return

                if self.effect[i]:
                    view.children[9].style = disnake.ButtonStyle.gray
                    await player.clear_filters(fast_apply=True)
                    self.effect[i] = False
                    if player.is_looping:
                        view.children[8].emoji = emojis['onLoopMode']
                        view.children[8].style = disnake.ButtonStyle.blurple
                    await player.controller.edit(view=view)
                    return

        if inter.data['custom_id'] == 'volumem:10':
            if await self.cheks(inter, player):

                player.volume -= 10
                await player.set_volume(player.volume)

                await self.volume_blocked(player)
                if player.is_looping:
                    view.children[8].emoji = emojis['onLoopMode']
                    view.children[8].style = disnake.ButtonStyle.blurple
                if self.effect[inter.guild.id]:
                    view.children[9].style = disnake.ButtonStyle.red
                await player.controller.edit(embed=await self.playerMessage(player))

        if inter.data['custom_id'] == 'page_modal':
            try:
                await inter.response.edit_message(
                    embed=player.pages[int(dict(inter.text_values.items()).get('page_num')) - 1],
                    components=await self.make_buttons(0, len(player.pages))
                )
            except IndexError:
                return await inter.response.send_message(f"Страница не сущевствует! Укажите число в диапазоне от 1 до {len(player.pages)}", ephemeral=True)


    @components.button_listener()
    async def hey_listen(self, inter: disnake.MessageInteraction, *,
        page: int,
        where,
        pages: int,
    ):
        player = inter.guild.voice_client
        if where == "stop":
            await inter.response.send_modal(
                title="Перейти к странице",
                custom_id="page_modal",
                components=[
                    disnake.ui.TextInput(
                        label="Страница",
                        placeholder="Укажите номер страницы",
                        custom_id="page_num",
                        style=disnake.TextInputStyle.short,
                        max_length=3,
                    ),
                ],
            )
            return

        page = (page + 1 if where == "next" else page - 1) % pages
        await inter.response.edit_message(
            embed=player.pages[page],
            components=await self.make_buttons(page, pages),
        )


    @commands.slash_command(
        description="🎶 Воспроизвести музыку в голосовом канале",
        dm_permission=False
    )
    async def play(
        self,
        inter: disnake.ApplicationCommandInteraction,
        search: str = commands.Param(
            name="название",
            description="название трека"
        )
    ) -> None:
        await inter.response.defer()
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        try:
            if not inter.author.voice:
                await inter.response.send_message(
                    "Вы должны присоединиться к голосовому каналу, чтобы начать прослушивание музыки!",
                    ephemeral=True
                    )
            if not inter.guild.voice_client:
                player = await inter.user.voice.channel.connect(cls=Player)
            else:
                player: Player = inter.guild.voice_client

            service_blacklist = ["www.youtube.com", "youtu.be", "twitch.tv"]
            if any(service in search for service in service_blacklist):
                await inter.send(
                    "Данный сервис не поддерживается, используйте другой!", 
                    ephemeral=True
                )
                return

            voice_state = inter.author.voice.channel.id
            voice_channel = getattr(inter.user.voice, 'channel', inter.guild.voice_client)
            await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)

            if inter.guild.voice_client:
                voice_client = inter.guild.voice_client.channel.id
                if voice_state != voice_client:
                    await inter.send(
                        f"Я уже играю музыку в канале {inter.guild.voice_client.channel.mention}, присоединитесь к этому каналу, чтобы получить доступ для управления плеером",
                        ephemeral=True
                    )
                    return

            tracks = await player.fetch_tracks(search, mafic.SearchType.SOUNDCLOUD)
            if not tracks:
                await inter.send("Трек по вашему запросу не найден", ephemeral=True)
                return

            self.effect.setdefault(inter.guild.id, False)
            if isinstance(tracks, mafic.Playlist):
                for track in tracks.tracks:
                    player.queue.append(track)

                if player.current:
                    message_controller_id = player.controller_id
                    try:
                        await inter.channel.fetch_message(int(message_controller_id))
                        await inter.delete_original_response(delay=6)
                    except (disnake.NotFound, disnake.Forbidden):
                        try:
                            message = self.bot.get_message(int(message_controller_id))
                            if message is not None:
                                await message.delete()
                        except (disnake.NotFound, disnake.Forbidden):
                            ...

                    embed = disnake.Embed(
                        description=f"Плейлист `{tracks.name}` добавлен в очередь! (`{len(tracks.tracks)} Треков`)",
                        color=0x2b2d31
                    )
                    embed.set_author(
                        name=f"{inter.user.name} Добавляет плейлист в очередь",
                        icon_url=inter.author.display_avatar
                    )
                    await inter.send(embed=embed, delete_after=5)
                    return
                else:
                    try:
                        await inter.channel.fetch_message(player.controller_id)
                        await player.controller.edit(embed=await self.playerMessage(player))
                    except:
                        await player.play(player.queue[0])
                        player.controller = await inter.edit_original_response(
                            embed=await self.playerMessage(player), 
                            view=MusicButtons()
                        )
                        player.controller_id = player.controller.id

                    await self.update_embed(player)

            else:
                tracks = await player.fetch_tracks(search, mafic.SearchType.SOUNDCLOUD)
                track = tracks[0]
                if player.current:
                    try:
                        await inter.channel.fetch_message(int(player.controller_id))
                        await inter.delete_original_response(delay=6)
                    except (disnake.NotFound, disnake.Forbidden):
                        try:
                            message = self.bot.get_message(int(player.controller_id))
                            if message is not None:
                                await message.delete()
                        except (disnake.NotFound, disnake.Forbidden):
                            ...
                    player.queue.append(track)
                    message = {
                        'ru': f'Трек под названием **{track.title}** (`{int(track.length / 1000 / 60)}:{str(track.length / 1000)[:2]}`) был добавлен в очередь',
                        'en': f'The track called **{track.title}** (`{int(track.length / 1000 / 60)}:{str(track.length / 1000)[:2]}`) has been added to the queue',
                        'uk': f'Трек під назвою **{track.title}** (`{int(track.length / 1000 / 60)}:{str(track.length / 1000)[:2]}`) додано до черги'
                    }[lang_server]
                    embed = disnake.Embed(
                        description=message,
                        color=0x2b2d31
                    )
                    embed.set_author(
                        name=f"{inter.user.name} Добавляет трек в очередь",
                        icon_url=inter.author.display_avatar
                    )
                    embed.set_thumbnail(url=track.artwork_url)
                    await inter.edit_original_response(embed=embed, components=[])
                else:
                    player.queue.append(track)
                    await player.play(track)

                    try:
                        await inter.channel.fetch_message(int(player.controller_id))
                        await player.controller.edit(embed=await self.playerMessage(player))
                    except:
                        player.controller = await inter.edit_original_response(
                            embed=await self.playerMessage(player), view=MusicButtons()
                        )
                        player.controller_id = player.controller.id

                    await self.update_embed(player)

        except Exception as e:
            print(e)
            message = {
                'ru': 'Неизвестный формат трека. Пожалуйста, предоставьте ссылку на трек в Soundcloud или введите название трека',
                'en': 'Unknown track format. Please provide a link to the track on Soundcloud or enter the track name',
                'uk': 'Невідомий формат треку. Будь ласка, надайте посилання на трек у Soundcloud або введіть назву треку'
            }[lang_server]
            await inter.send(message, ephemeral=True)

    @play.autocomplete("название")
    async def autoplay(self, inter: disnake.ApplicationCommandInteraction, string: str):
        if string is None:
            return
            
        tracks = await self.bot.node.fetch_tracks(string, search_type = mafic.SearchType.SOUNDCLOUD)
        if isinstance(tracks, mafic.Playlist):
            return [disnake.OptionChoice(name=f"{tracks.name} ({len(tracks.tracks)} Треков)", value=string[:100])]

        return [disnake.OptionChoice(name=track.title, value=track.uri[:100]) for track in tracks]

    @commands.slash_command(description="🎶 Музыка | Остановить плеер")
    async def stop(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        player = inter.guild.voice_client
        if not player:
            return await inter.send("Музыка сейчас не играет", ephemeral=True)
        await player.destroy()
        await inter.send("Плеер был остановлен")

    @commands.slash_command(description="🎶 Музыка | Настройка громкости")
    async def volume(self, inter: disnake.ApplicationCommandInteraction, volume: commands.Range[int, 0, 200] = commands.Param(
        name="громкость",
        description="Вы можете установить громкость в диапозоне от 0 до 200"
    )):
        await inter.response.defer()
        lang = db.get(f"lang_{inter.guild.id}") or "ru"
        player = inter.guild.voice_client
        if not player:
            message = {
                'ru': 'Музыка сейчас не играет',
                'en': 'Music is not playing now',
                'uk': 'Музика зараз не грає'
            }[lang]
            return await inter.send(message, ephemeral=True)

        if inter.author.voice is None or inter.author.voice.channel is None:
            message = {
                'ru': 'Вы должны находиться в голосовом канале что бы использовать эту команду!',
                'en': 'You must be in a voice channel to use this command!',
                'uk': 'Ви повинні знаходитися в голосовому каналі, щоб використовувати цю команду!'
            }[lang]
            return await inter.send(message, ephemeral=True)

        await player.set_volume(volume)
        player.volume = volume
        message = {
            'ru': f'Громкость плеера установлена на {volume}%',
            'en': f'Player volume set to {volume}%',
            'uk': f'Гучність плеєра встановлена на {volume}%'
        }[lang]
        await self.volume_blocked(player)
        await inter.send(message, ephemeral=True)

    async def update_embed(self, player):
        while not player.paused and player.current:
            try:
                await player.controller.edit(embed=await self.playerMessage(player))
            except (disnake.NotFound, disnake.Forbidden):
                return
            await asyncio.sleep(6)

    async def playerMessage(self, player):
        lang_server = db.get(f"lang_{player.guild.id}") or "ru"

        track = player.current
        i = player.guild.id
        loop = player.is_looping
        volume = player.volume
        qsize = len(player.queue)
        embed = disnake.Embed(color=0x2b2d31)
        embed.set_thumbnail(url=track.artwork_url)
        emoji = '🔇' if volume == 0 else '🔊'
        text = '⏸️' if player.paused else '▶️'
        self.oh.setdefault(i, [])
        [self.oh[player.guild.id].append(track.title) for track in player.queue]
        t_max, t_cur, ost_time, odur, dur, hours, pos, timed, remainder = None, None, None, None, None, None, None, None, None
        duration: int = None
        positionbar = None
        source_links = {
            "soundcloud": "https://cdn.discordapp.com/attachments/1151406452611751936/1179092868879618069/Soundcloud-Logo-Png-Transparent-Background.png?ex=657886ce&is=656611ce&hm=d1fdc1a6eb62e35f6cd354c09e22bf7eb39845804c91d181c6465b771fb1f9bb&",
            "spotify": "https://media.discordapp.net/attachments/1151406452611751936/1181268593409789983/gifdark_spotify.PNG?ex=6580711b&is=656dfc1b&hm=f8b4f6e73191ba1ea41cb58163f747fa5c4a83f88fab3af090bc4d5b939e9e2a&=&format=webp&quality=lossless",
            "bandcamp": "https://cdn.discordapp.com/attachments/1151406452611751936/1182206326999363635/92-920204_bandcamp-logo-circle.png?ex=6583da70&is=65716570&hm=32c3bc7517ef2b281d5dcf0b4f00fbfec9181307d934237fbf20dd3e0f116635&",
            "yandexmusic": "https://cdn.discordapp.com/attachments/1151406452611751936/1181647289471729664/52c887278299.png?ex=6581d1cb&is=656f5ccb&hm=4dbe41f30879aa6c9133c42f0d23432bef3e36274dfa4b4012dc4bb6aea51eb8&",
        }
        searchtype = None
        if track and track.source:
            searchtype = source_links.get(track.source)
        if track.stream:
            positionbar = f"<:1_:1083430189368877168>{posEmoji * 10}<:224:1160530351505035357>"
            timed = "🔴 Трансляция"
            odur = ""

        else:
            t_cur = player.position / 1000
            t_max = track.length / 1000
            ost_time = t_max - t_cur
            pos = int(7 * t_cur / t_max)
            dur = sum([t_max for track in player.queue])
            hours, remainder = divmod(dur, 3600)
            odur = f"`{time.strftime('%M:%S', time.gmtime(ost_time))}`"
            duration = time.strftime('%M:%S', time.gmtime(t_max))
            timed = f"{time.strftime('%M:%S', time.gmtime(t_cur))} / {duration}"
            if ost_time < 4:
                positionbar = f"<:1_:1083430189368877168>{posEmoji * 7}<:224:1160530351505035357>"
            else:
                positionbar = f"<:1_:1083430189368877168>{posEmoji * pos}{leftEmoji * (7 - pos)}<:2_:1083430191944171521>"

        if lang_server == 'ru':
            durations_track = f"`{int(hours)} ч. {int(time.strftime('%M', time.gmtime(remainder)))} мин.`" if hours else f"`{int(time.strftime('%M', time.gmtime(remainder)))} мин.`"

            embed.set_author(
                name=f"Сейчас играет: {player.current.title}",
                icon_url=searchtype
            )
            text1 = '**✨ В очереди пусто! Добавьте что нибудь 🎵**'
            if qsize == 2:
                if loop:
                    text1 = f'В очереди: **{track.title}** и ещё 1 трек ({durations_track})'
                else:
                    text1 = f'В очереди: **{track.title if loop else self.oh[i][1]}** ({durations_track})'
            elif qsize == 3:
                text1 = f'В очереди: **{track.title if loop else self.oh[i][1]}**, и ещё 2 трека ({durations_track})'
            elif qsize >= 4:
                text1 = f'В очереди: **{track.title if loop else self.oh[i][1]}**, и ещё {qsize - 1} трек{"a" if qsize == 3 else "ов"} ({durations_track})'

            embed.set_footer(
               text=f"Музыкальный сервер: Tyad "
                    f" -  Нагрузка: {int(player.node.stats.cpu.system_load)}%  - "
                    f" Подключений: {player.node.stats.playing_player_count}"
            )
            embed.description = f"\n\n{text} `{timed}` {positionbar} {odur} `{emoji} {volume}%` \n\n{text1}\n"
            embed.description = embed.description[:2048]
        if lang_server == 'en':
            durations_track = f"`{int(hours)} h. {int(time.strftime('%M', time.gmtime(remainder)))} min.`" if hours else f"`{int(time.strftime('%M', time.gmtime(remainder)))} min.`"
            embed.set_author(
                name=f"Now playing: {player.current.title}",
                icon_url=searchtype
            )
            text1 = ''
            if qsize == 2:
                if loop:
                    text1 = f'Queue: **{track.title}**, and 1 more track ({durations_track})'
                else:
                    text1 = f'Queue: **{self.oh[i][0]}** ({durations_track})'
            elif qsize == 3:
                text1 = f'Queue: **{track.title if loop else self.oh[i][0]}**, and 2 more track ({durations_track})'
            elif qsize >= 4:
                text1 = f'Queue: **{track.title if loop else self.oh[i][0]}**, and {qsize - 1} more tracks{"s" if qsize == 3 else "s"} ({durations_track})'

            embed.set_footer(
                text=f"Lavalink server: Tyad "
                     f" Connections:  {self.bot.node.player_count}"
            )
            embed.description = f"\n\n{text} `{timed}` {positionbar} `{odur}` `{emoji} {volume}%` \n\n{text1}\n"
        if lang_server == 'uk':
            durations_track = f"`{int(hours)} ч. {int(time.strftime('%M', time.gmtime(remainder)))} мин.`" if hours else f"`{int(time.strftime('%M', time.gmtime(remainder)))} мин.`"
            embed.set_author(
                name=f"Зараз грає: {player.current.title}",
                icon_url=searchtype
            )
            text1 = ''
            if qsize == 1:
                text1 = f'В черзі: **{self.oh[i][0]}** ({durations_track})'
            elif qsize == 2:
                text1 = f'В черзі: **{self.oh[i][0]}**, та ще 2 трек ({durations_track})'
            elif qsize >= 3:
                text1 = f'В черзі: **{self.oh[i][0]}**, і ще {qsize - 1} трек{"и" if qsize == 3 else "ів"} ({durations_track})'

            embed.set_footer(
                text=f"Музичний сервер: Tyad "
                     f"Підключень:  {self.bot.node.player_count}"
            )
            embed.description = f"\n\n{text} `{timed}` {positionbar} `{odur}` `{emoji} {volume}%` \n\n{text1}\n"
        del self.oh[i]
        return embed


def setup(bot):
    bot.add_cog(Music(bot))
