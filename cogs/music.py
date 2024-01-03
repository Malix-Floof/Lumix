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

import time
import mafic
import disnake

from random import shuffle
from disnake.ext import components, commands, tasks
from utils import *
from db import SQLITE
from config import playerSettings, emojis
from mafic import (
    NodePool,
    Player,
    Playlist,
    Track,
    TrackEndEvent
)

db = SQLITE("music.db")

class Music(commands.Cog):
    def __init__(self, bot, *args, **kwargs):
        self.bot = bot
        self.oh = {}
        self.message_controller: dict[disnake.Message] = {}
        self.effect: dict[bool] = {}
        self.queues: dict[Track] = {}
        self.loop: dict[bool] = {}

    async def destroy(self, player):
        await player.disconnect()
        self.update_embed.cancel()
        message = self.message_controller.get(player.guild.id)
        if message:
            await message.edit(components=[])
        db.set(f"message_controller_{player.guild.id}", "0")
        i = player.guild.id
        self.queues.pop(i, None)
        self.loop.pop(i, None)
        self.message_controller.pop(i, None)
        self.oh.pop(i, None)
        self.effect.pop(i, None)

    @commands.Cog.listener()
    async def on_track_end(self, event: TrackEndEvent):
        if self.queues.get(event.player.guild.id):
            if self.loop.get(event.player.guild.id):
                await event.player.play(self.queues[event.player.guild.id][0])
            else:
                await event.player.play(self.queues[event.player.guild.id].pop(0))
        else:
            message = self.message_controller.get(event.player.guild.id)
            if message:
                await message.edit(components=[])

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        player = member.guild.voice_client
        if player is None:
            return
        
        if not any(not member.bot for member in player.channel.members):
            return await self.destroy(player)

        if member.id == self.bot.user.id and after.channel is None:
            return await self.destroy(player)

    @commands.Cog.listener("on_button_click")
    @commands.Cog.listener("on_component")
    async def interaction(self, inter):
        if not inter.data.custom_id.startswith("musicplayer_"):
            return

        await self.player_controller(inter, inter.data.custom_id)

    @commands.Cog.listener()
    async def on_ready(self):
        print("music.py is ready")

    async def set_loop(self, player):
        components = CONTROLLER_BUTTON
        components[7].custom_id = PlayerControls.ON_LOOP_MODE if self.loop[
                                                                     player.guild.id] is True else PlayerControls.LOOP_MODE
        components[7].emoji = emojis['onLoopMode'] if self.loop[player.guild.id] is True else emojis['loopEmoji']
        components[7].style = ButtonStyle.blurple if self.loop[player.guild.id] is True else ButtonStyle.gray
        await self.message_controller[player.guild.id].edit(components=components)

    async def set_paused(self, player):
        components = CONTROLLER_BUTTON
        disable_buttons = [0, 2, 3, 4, 5, 6, 7, 8, 9]
        if player.paused:
            for button in disable_buttons:
                components[button].disabled = False
            components[1].custom_id = PlayerControls.PAUSE
            components[1].emoji = emojis['pauseEmoji']
            components[1].style = ButtonStyle.gray
            await player.resume()
            self.update_embed.start(player)
        else:
            for button in disable_buttons:
                components[button].disabled = True
            components[1].custom_id = PlayerControls.PLAY
            components[1].emoji = emojis['playEmoji']
            components[1].style = ButtonStyle.blurple
            await player.pause()
            self.update_embed.cancel()
        await self.message_controller[player.guild.id].edit(components=components)

    async def bassboost(self, player):
        components = CONTROLLER_BUTTON
        if self.effect[player.guild.id] is False:
            components[8].style = ButtonStyle.red
            karaoke = mafic.Karaoke(3, 3)
            self.effect[player.guild.id] = True
            await player.add_filter(mafic.Filter(karaoke=karaoke), label="karaoke", fast_apply=True)
            await self.message_controller[player.guild.id].edit(components=components)
            return
        if self.effect[player.guild.id]:
            components[8].style = ButtonStyle.gray
            await player.clear_filters(fast_apply=True)
            self.effect[player.guild.id] = False
            await self.message_controller[player.guild.id].edit(components=components)
            return

    async def player_controller(self, inter, control: str):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        player = inter.guild.voice_client
        if player:
            match control:
                case PlayerControls.BACK:
                    await player.seek(0)
                    message = {
                        'ru': 'Трек перемотан на начало',
                        'en': 'Track rewound to the beginning',
                        'uk': 'Трек перемотаний на початок'
                    }[lang_server]
                    await inter.send(message, ephemeral=True)
                case PlayerControls.PLAY:
                    await self.set_paused(player)
                    message = {
                        'ru': f'{inter.author.name} снял(-а) трек с паузы',
                        'en': f'{inter.author.name} unpaused the track',
                        'uk': f'{inter.author.name} зняв(-ла) трек із паузи'
                    }[lang_server]
                    await inter.send(message)
                case PlayerControls.SKIP:
                    if self.loop[inter.guild.id] == True:
                        self.loop[inter.guild.id] = False
                        await player.stop()
                        self.loop[inter.guild.id] = True
                    else:
                        await player.stop()
                    message = {
                        'ru': f'{inter.author.name} пропустил(-а) трек {player.current.title}',
                        'en': f'{inter.author.name} missed a track {player.current.title}',
                        'uk': f'{inter.author.name} пропустив(-ла) трек {player.current.title}'
                    }[lang_server]
                    await inter.send(message)
                case PlayerControls.PAUSE:
                    await self.set_paused(player)
                    message = {
                        'ru': f'{inter.author.name} поставил(-а) трек на паузу',
                        'en': f'{inter.author.name} pause the track',
                        'uk': f'{inter.author.name} поставив(-ла) трек на паузу'
                    }[lang_server]
                    await inter.send(message)
                case PlayerControls.STOP:
                    message = {
                        'ru': f'Плеер был остановлен: {inter.author.name}',
                        'en': f'The player has been stopped: {inter.author.name}',
                        'uk': f'Плеєр було зупинено: {inter.author.name}'
                    }[lang_server]
                    await self.destroy(player)
                case PlayerControls.SHUFFLE:
                    if len(self.queues[inter.guild.id]) < 3:
                        message = {
                            'ru': 'Мало треков в очереди! Требуется как минимум 3',
                            'en': 'Few tracks in the queue! Requires at least 3',
                            'uk': 'Мало треків у черзі! Потрібно як мінімум 3'
                        }[lang_server]
                        return await inter.send(message, ephemeral=True)
                    shuffle(self.queues[inter.guild.id])
                    message = {
                        'ru': 'Очередь была перемешана',
                        'en': 'The queue has been jumbled',
                        'uk': 'Черга була перемішана'
                    }[lang_server]
                    await inter.send(message, ephemeral=True)
                case PlayerControls.LOOP_MODE:
                    self.loop[inter.guild.id] = True
                    await self.set_loop(player)
                    message = {
                        'ru': 'Повтор трека был включен',
                        'en': 'Track repeat has been turned on',
                        'uk': 'Повторення треку було вкнено'
                    }[lang_server]
                    await inter.send(message, ephemeral=True)
                case PlayerControls.ON_LOOP_MODE:
                    self.loop[inter.guild.id] = False
                    await self.set_loop(player)
                    message = {
                        'ru': 'Повтор трека был выключен',
                        'en': 'Track repeat has been turned off',
                        'uk': 'Повторення треку було вимкнено'
                    }[lang_server]
                    await inter.send(message, ephemeral=True)
                case PlayerControls.VOLUMEM:
                    message = {
                        'ru': 'Данная возможность появится в будущем...',
                        'en': 'This feature will appear in the future...',
                        'uk': 'Ця можливість з\'явиться в майбутньому...'
                    }[lang_server]
                    await inter.send(message, ephemeral=True)
                case PlayerControls.VOLUMEP:
                    '''volume = player.volume
                    await player.set_volume(volume + 10)
                    message = {
                        'ru': f'Громкость увеличена на 10%, текущая громкость: {player.volume}%',
                        'en': f'Volume increased by 10%, current volume: {player.volume}%',
                        'uk': f'Гучність збільшена на 10%, поточна гучність: {player.volume}%'
                    }[lang_server]
                    await inter.send(message, ephemeral=True)'''
                    message = {
                        'ru': 'Данная возможность появится в будущем...',
                        'en': 'This feature will appear in the future...',
                        'uk': 'Ця можливість з\'явиться в майбутньому...'
                    }[lang_server]
                    await inter.send(message, ephemeral=True)
                case PlayerControls.PLAYLIST:
                    track = player.current
                    duraction = track.length / 1000
                    durations = sum([duraction for track in self.queues[inter.guild.id]])
                    qsize = len(self.queues[inter.guild.id])
                    queue = '\n'.join([
                        f"{i + 1}. `{time.strftime('%M:%S', time.gmtime(track.length / 1000))}` - [{track.title}]({track.uri})"
                        for i, track in
                        list(enumerate(self.queues[inter.guild.id]))[:min(len(self.queues[inter.guild.id]), 30)]
                    ])
                    embed = disnake.Embed(color=0x2b2d31)
                    message = {
                        'ru': f'ID сесси: {player.node.session_id}',
                        'en': f'Session ID: {player.node.session_id}',
                        'uk': f'ID сесії: {player.node.session_id}'
                    }[lang_server]
                    embed.set_footer(text=message, icon_url=inter.user.avatar)
                    hours, remainder = divmod(durations, 3600)
                    if hours == 0:
                        message = {
                            'ru': f'`{int(time.strftime("%M", time.gmtime(remainder)))} мин.`',
                            'en': f'`{int(time.strftime("%M", time.gmtime(remainder)))} min.`',
                            'uk': f'`{int(time.strftime("%M", time.gmtime(remainder)))} хв.`'
                        }[lang_server]
                        durations = message
                    else:
                        if lang_server == 'ru':
                            durations = f"`{int(hours)} ч. {int(time.strftime('%M', time.gmtime(remainder)))} мин.`"
                        if lang_server == 'en':
                            durations = f"`{int(hours)} h. {int(time.strftime('%M', time.gmtime(remainder)))} min.`"
                        if lang_server == 'uk':
                            durations = f"`{int(hours)} год. {int(time.strftime('%M', time.gmtime(remainder)))} хв.`"
                    if lang_server == 'ru':
                        ixi = f"И ещё {qsize - 50} треков..." if qsize > 50 else ""
                        embed.description = f"{qsize} трек(-ов), примерное время {durations} \n\n{queue}\n\n{ixi}"
                    if lang_server == 'en':
                        ixi = f"And more {qsize - 50} tracks..." if qsize > 50 else ""
                        embed.description = f"{qsize} track(s), estimated time {durations} \n\n{queue}\n\n{ixi}"
                    if lang_server == 'uk':
                        ixi = f"І ще {qsize - 50} треків..." if qsize > 50 else ""
                        embed.description = f"{qsize} трек(-ів), зразковий час {durations} \n\n{queue}\n\n{ixi}"
                    await inter.send(embed=embed, ephemeral=True)
                case PlayerControls.BASSBOOST:
                    await self.bassboost(player)
                    if self.effect[player.guild.id] is False:
                        message = {
                            'ru': 'Установлен фильтр "Обычный"',
                            'en': 'Set filter "Default"',
                            'uk': 'Встановлено фільтр "Звичайний"'
                        }[lang_server]
                        await inter.send(message, ephemeral=True)
                    if self.effect[player.guild.id]:
                        message = {
                            'ru': 'Установлен фильтр "Бас буст"',
                            'en': 'Set filter "Bass Boost"',
                            'uk': 'Встановлено фільтр "Бас буст"'
                        }[lang_server]
                        await inter.send(message, ephemeral=True)

    @commands.slash_command(description="🎶 Музыка | Воспроизвести музыку в голосовом канале", dm_permission=False)
    async def play(self, inter, search: str = commands.Param(name="название", description="название трека")):
        await inter.response.defer()
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        if not inter.author.voice:
            return await inter.send("Вы должны присоединиться к голосовому каналу, чтобы начать прослушивание музыки!",
                                    ephemeral=True)
        try:
            if not inter.guild.voice_client:
                player = await inter.user.voice.channel.connect(cls=mafic.Player)
            else:
                player = inter.guild.voice_client

            service_blacklist = ["www.youtube.com", "youtu.be", "twitch.tv"]
            if any(service in search for service in service_blacklist):
                return await inter.send("Данный сервис не поддерживается, используйте другой!", ephemeral=True)

            voice_state = inter.author.voice.channel.id
            voice_channel = getattr(inter.user.voice, 'channel', inter.guild.voice_client)
            await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)

            if inter.guild.voice_client:
                voice_client = inter.guild.voice_client.channel.id
                if voice_state != voice_client:
                    return await inter.send(
                        f"Я уже играю музыку в канале {inter.guild.voice_client.channel.mention}, присоединитесь к этому каналу, чтобы получить доступ для управления плеером",
                        ephemeral=True)

            tracks = await player.fetch_tracks(search, mafic.SearchType.SOUNDCLOUD)
            self.queues.setdefault(inter.guild.id, [])
            self.effect.setdefault(inter.guild.id, [])
            self.effect[inter.guild.id] = False
            if isinstance(tracks, mafic.Playlist):
                for i in tracks.tracks:
                    if player.current:
                        self.queues[inter.guild.id].append(i)
                    else:
                        self.queues[inter.guild.id].append(i)
                        await player.play(self.queues[inter.guild.id][0])

                self.loop.setdefault(inter.guild.id, False)
                self.message_controller.setdefault(inter.guild.id, [])
                components = CONTROLLER_BUTTON
                components[1].custom_id = PlayerControls.PAUSE
                components[1].emoji = emojis['pauseEmoji']
                try:
                    message_controller_id = db.get(f"message_controller_{inter.guild.id}") or "0"
                    await inter.channel.fetch_message(message_controller_id)
                    await self.message_controller[inter.guild.id].edit(embed=self.playerMessage(player))
                except:
                    channel = self.bot.get_channel(inter.channel.id)
                    self.message_controller[inter.guild.id] = await channel.send(embed=self.playerMessage(player),
                                                                                 components=components)

                    message_controller_id = db.set(f"message_controller_{inter.guild.id}",
                                                   f"{self.message_controller[inter.guild.id].id}")
                if not self.update_embed.is_running():
                    self.update_embed.start(player)

                embed = disnake.Embed(
                    description=f"Плейлист `{tracks.name}` добавлен в очередь! (`{len(tracks.tracks)} Треков`)",
                    color=0x2b2d31
                )
                return await inter.send(embed=embed)

            if not tracks:
                return await inter.send(
                    "Трек по вашему запросу не найден. Для более точного поиска, пожалуйста, укажите ссылку на SoundCloud трек или укажите автора с названием трека, например: `Nikitata Escord`",
                    ephemeral=True
                )

            options = [
                disnake.SelectOption(
                    label=track.title[:25],
                    description=f"{int(track.length / 1000 / 60)}:{str(track.length / 1000)[:2]}",
                    value=str(track.uri[:100])) for track in tracks[:25]
            ]
            try:
                music = disnake.ui.Select(
                    placeholder="Выберите трек для воспроизведения",
                    options=options,
                    custom_id=await self.music.build_custom_id()
                )
                await inter.send("Выберите трек:", components=[music])
            except:
                return await inter.send(
                    "Трек по вашему запросу не найден. Для более точного поиска, пожалуйста, укажите ссылку на SoundCloud трек или укажите автора с названием трека, например: `Nikitata Escord`",
                    ephemeral=True)
        except mafic.TrackLoadException:
            message = {
                'ru': 'Неизвестный формат трека. Пожалуйста, предоставьте ссылку на трек в Soundcloud или введите название трека',
                'en': 'Unknown track format. Please provide a link to the track on Soundcloud or enter the track name',
                'uk': 'Невідомий формат треку. Будь ласка, надайте посилання на трек у Soundcloud або введіть назву треку'
            }[lang_server]
            await inter.send(message, ephemeral=True)

    @components.select_listener()
    async def music(self, inter: disnake.Interaction):
        await inter.response.defer()
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"

        if not inter.guild.voice_client:
            player = await inter.user.voice.channel.connect(cls=mafic.Player)
        else:
            player = inter.guild.voice_client

        voice_channel = getattr(inter.user.voice, 'channel', inter.guild.voice_client)
        await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)
        track = await player.fetch_tracks(inter.values[0], mafic.SearchType.SOUNDCLOUD)
        track = track[0]
        if player.current:
            self.queues[inter.guild.id].append(track)
        else:
            await player.play(track)

        message = {
            'ru': f'Трек под названием **{track.title}** (`{int(track.length / 1000 / 60)}:{str(track.length / 1000)[:2]}`) был добавлен в очередь',
            'en': f'The track called **{track.title}** (`{int(track.length / 1000 / 60)}:{str(track.length / 1000)[:2]}`) has been added to the queue',
            'uk': f'Трек під назвою **{track.title}** (`{int(track.length / 1000 / 60)}:{str(track.length / 1000)[:2]}`) додано до черги'
        }[lang_server]

        embed = disnake.Embed(
            description=message,
            color=0x2b2d31
        )
        await inter.edit_original_response(content="", embed=embed, components=[])
        self.queues.setdefault(inter.guild.id, [])
        self.loop.setdefault(inter.guild.id, False)
        self.message_controller.setdefault(inter.guild.id, [])
        components = CONTROLLER_BUTTON
        components[1].custom_id = PlayerControls.PAUSE
        components[1].emoji = emojis['pauseEmoji']
        try:
            message_controller_id = db.get(f"message_controller_{inter.guild.id}") or "0"
            await inter.channel.fetch_message(message_controller_id)
            await self.message_controller[inter.guild.id].edit(embed=self.playerMessage(player))
        except:
            channel = self.bot.get_channel(inter.channel.id)
            self.message_controller[inter.guild.id] = await channel.send(embed=self.playerMessage(player),
                                                                         components=components)

            message_controller_id = db.set(f"message_controller_{inter.guild.id}",
                                           f"{self.message_controller[inter.guild.id].id}")
        if not self.update_embed.is_running():
            self.update_embed.start(player)

    @commands.slash_command(description="🎶 Музыка | Остановить плеер")
    async def stop(self, inter):
        player = inter.guild.voice_client
        if not player:
            return await inter.send("Музыка сейчас не играет", ephemeral=True)
        await self.destroy(player)
        await inter.send("Плеер был остановлен")

    @commands.slash_command(description="🎶 Музыка | Настройка громкости")
    async def volume(self, inter, volume: commands.Range[int, 0, 200] = commands.Param(
        name="громкость",
        description="Вы можете установить громкость в диапозоне от 0 до 200"
    )):
        await inter.response.defer()
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        player = inter.guild.voice_client
        if not player:
            message = {
                'ru': 'Музыка сейчас не играет',
                'en': 'Music is not playing now',
                'uk': 'Музика зараз не грає'
            }[lang_server]
            return await inter.send(message, ephemeral=True)

        '''        
        if inter.author.voice is None or inter.author.voice.channel is None:
            message = {
                'ru': 'Вы должны находиться в голосовом канале что бы использовать эту команду!',
                'en': 'You must be in a voice channel to use this command!',
                'uk': 'Ви повинні знаходитися в голосовому каналі, щоб використовувати цю команду!'
            }[lang_server]
            return await inter.send(message, ephemeral=True)'''

        await player.set_volume(volume)
        message = {
            'ru': f'Громкость плеера установлена на {volume}%',
            'en': f'Player volume set to {volume}%',
            'uk': f'Гучність плеєра встановлена на {volume}%'
        }[lang_server]
        db.set(f"volume_{player.guild.id}", f"{volume}")
        await inter.send(message, ephemeral=True)

    @tasks.loop(seconds=playerSettings['playerEditSeconds'])
    async def update_embed(self, player):
        try:
            await self.message_controller[player.guild.id].edit(embed=self.playerMessage(player))
        except (disnake.NotFound, disnake.Forbidden):
            return

    def playerMessage(self, player):
        track = player.current
        volu = db.get(f"volume_{player.guild.id}") or "100"
        volume = int(volu)
        qsize = len(self.queues[player.guild.id])
        embed = disnake.Embed(color=0x2b2d31)
        emoji = '🔇' if int(volume) == 0 else '🔊'
        text = '⏸️' if player.paused else '▶️'
        self.oh.setdefault(player.guild.id, [])
        [self.oh[player.guild.id].append(track.title) for track in self.queues[player.guild.id]]
        lang_server = db.get(f"lang_{player.guild.id}") or "ru"
        duraction = track.length / 1000
        if lang_server == 'ru':
            dur = sum([duraction for track in self.queues[player.guild.id]])
            hours, remainder = divmod(dur, 3600)
            durations_track = f"`{int(hours)} ч. {int(time.strftime('%M', time.gmtime(remainder)))} мин.`" if hours else f"`{int(time.strftime('%M', time.gmtime(remainder)))} мин.`"
            embed.set_author(
                name=f"Сейчас играет: {player.current.title}",
            )
            text1 = ''
            if qsize == 2:
                if self.loop[player.guild.id]:
                    text1 = f'В очереди: **{track.title}** и ещё 1 трек ({durations_track})'
                if self.loop[player.guild.id] is False:
                    text1 = f'В очереди: **{track.title if self.loop[player.guild.id] else self.oh[player.guild.id][1]}** ({durations_track})'
            elif qsize == 3:
                text1 = f'В очереди: **{track.title if self.loop[player.guild.id] else self.oh[player.guild.id][1]}**, и ещё 2 трека ({durations_track})'
            elif qsize >= 4:
                text1 = f'В очереди: **{track.title if self.loop[player.guild.id] else self.oh[player.guild.id][1]}**, и ещё {qsize - 1} трек{"a" if qsize == 3 else "ов"} ({durations_track})'

            embed.set_footer(
               text=f"Музыкальный сервер: {player.node.label} "
                    f" -  Нагрузка: {int(player.node.stats.cpu.lavalink_load)}% "
                    f"Подключений: {player.node.stats.playing_player_count}"
            )
            t_cur = player.position / 1000
            t_max = track.length / 1000
            ost_time = t_max - t_cur
            odur = time.strftime('%M:%S', time.gmtime(ost_time))
            pos = int(playerSettings['playerProgressCount'] * t_cur / t_max)
            duration = time.strftime('%M:%S', time.gmtime(t_max))
            embed.description = f"\n\n{text} `{time.strftime('%M:%S', time.gmtime(t_cur))} / {duration}` <:1_:1083430189368877168>{TRACK_POSITION_EMBED_EMOJI * pos}" \
                                f"{TRACK_LEFT_EMOJI * (playerSettings['playerProgressCount'] - pos)}<:2_:1083430191944171521> `{odur}` `{emoji} {volume}%` \n\n{text1}\n"
        if lang_server == 'en':
            dur = sum([duraction for track in self.queues[player.guild.id]])
            hours, remainder = divmod(dur, 3600)
            durations_track = f"`{int(hours)} h. {int(time.strftime('%M', time.gmtime(remainder)))} min.`" if hours else f"`{int(time.strftime('%M', time.gmtime(remainder)))} min.`"
            embed.set_author(
                name=f"Now playing: {player.current.title}",
            )
            text1 = ''
            if qsize == 2:
                if self.loop[player.guild.id]:
                    text1 = f'Queue: **{track.title}**, and 1 more track ({durations_track})'
                if self.loop[player.guild.id] is False:
                    text1 = f'Queue: **{self.oh[player.guild.id][0]}** ({durations_track})'
            elif qsize == 3:
                text1 = f'Queue: **{track.title if self.loop[player.guild.id] else self.oh[player.guild.id][0]}**, and 2 more track ({durations_track})'
            elif qsize >= 4:
                text1 = f'Queue: **{track.title if self.loop[player.guild.id] else self.oh[player.guild.id][0]}**, and {qsize - 1} more tracks{"s" if qsize == 3 else "s"} ({durations_track})'

            embed.set_footer(
                text=f"Lavalink server: {player.node.identifier} "
                     f" -  Load CPU: {int(player.node.stats.cpu.lavalink_load)}% "
                     f"Connections: {player.node.stats.playing_players}"
            )
            t_cur = player.position / 1000
            t_max = track.length / 1000
            ost_time = t_max - t_cur
            odur = time.strftime('%M:%S', time.gmtime(ost_time))
            pos = int(playerSettings['playerProgressCount'] * t_cur / t_max)
            duration = time.strftime('%M:%S', time.gmtime(t_max))
            embed.description = f"\n\n{text} `{time.strftime('%M:%S', time.gmtime(t_cur))} / {duration}` <:1_:1083430189368877168>{TRACK_POSITION_EMBED_EMOJI * pos}" \
                                f"{TRACK_LEFT_EMOJI * (playerSettings['playerProgressCount'] - pos)}<:2_:1083430191944171521> `{odur}` `{emoji} {volume}%` \n\n{text1}\n"
        if lang_server == 'uk':
            dur = sum([duraction for track in self.queues[player.guild.id]])
            hours, remainder = divmod(dur, 3600)
            durations_track = f"`{int(hours)} ч. {int(time.strftime('%M', time.gmtime(remainder)))} мин.`" if hours else f"`{int(time.strftime('%M', time.gmtime(remainder)))} мин.`"
            embed.set_author(
                name=f"Зараз грає: {player.current.title}"
            )
            text1 = ''
            if qsize == 1:
                text1 = f'В черзі: **{self.oh[player.guild.id][0]}** ({durations_track})'
            elif qsize == 2:
                text1 = f'В черзі: **{self.oh[player.guild.id][0]}**, та ще 2 трек ({durations_track})'
            elif qsize >= 3:
                text1 = f'В черзі: **{self.oh[player.guild.id][0]}**, і ще {qsize - 1} трек{"и" if qsize == 3 else "ів"} ({durations_track})'

            embed.set_footer(
                text=f"Музичний сервер: {player.node.identifier}"
                     f"  -  Навантаження: {int(player.node.stats.cpu.lavalink_load)}%"
                     f" Підключень: {player.node.stats.playing_players}"
            )
            t_cur = player.position / 1000
            t_max = track.length / 1000
            ost_time = t_max - t_cur
            odur = time.strftime('%M:%S', time.gmtime(ost_time))
            pos = int(playerSettings['playerProgressCount'] * t_cur / t_max)
            duration = time.strftime('%M:%S', time.gmtime(t_max))
            embed.description = f"\n\n{text} `{time.strftime('%M:%S', time.gmtime(t_cur))} / {duration}` <:1_:1083430189368877168>{TRACK_POSITION_EMBED_EMOJI * pos}" \
                                f"{TRACK_LEFT_EMOJI * (playerSettings['playerProgressCount'] - pos)}<:2_:1083430191944171521> `{odur}` `{emoji} {volume}%` \n\n{text1}\n"
        del self.oh[player.guild.id]
        return embed


def setup(bot):
    bot.add_cog(Music(bot))
