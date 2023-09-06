import asyncio
import time
import async_timeout
import wavelink
from disnake.ext import commands, tasks
from config import playerSettings, emojis
from utils import PlayerControls, CONTROLLER_BUTTON, \
    TRACK_POSITION_EMBED_EMOJI, TRACK_LEFT_EMOJI, URL_REG
import disnake
from disnake import ButtonStyle
from db import SQLITE

db = SQLITE("database.db")


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.inter: disnake.MessageInteraction | disnake.Message = kwargs.get('inter', None)
        self.bot: commands.Bot = kwargs.get('bot', None)
        self.message_controller: disnake.Message | None = None
        self.message_controller_id: int = 0
        self.queue = asyncio.Queue()
        self.loop_mode = False
        self.waiting = False
        self.current = 0
        self.looped_track = None
        self.oh = None
        self.effect = False

    async def destroy(self, name: str):
        self.effect = False
        self.queue = None
        self.loop_mode = False
        self.looped_track = None
        self.update_embed.cancel()
        await self.resume()
        await self.stop()
        await self.disconnect()
        components = CONTROLLER_BUTTON
        for component in components:
            component.disabled = False
        components[1].style = ButtonStyle.gray
        components[5].style = ButtonStyle.gray
        components[9].style = ButtonStyle.gray
        components[1].emoji = emojis['pauseEmoji']
        components[5].emoji = emojis['loopEmoji']
        components[1].custom_id = PlayerControls.PAUSE
        await self.message_controller.edit(components=[])
        lang_server = db.get(f"lang_{self.inter.guild.id}") or "ru"
        if lang_server == 'ru':
            embed = disnake.Embed(title="Очередь закончена!", color=0x2b2d31)
        if lang_server == 'en':
            embed = disnake.Embed(title="The queue is over!", color=0x2b2d31)
        if lang_server == 'uk':
            embed = disnake.Embed(title="Черга закінчена!", color=0x2b2d31)
        embed.set_footer(text=name)
        await self.inter.send(embed=embed)

    async def bassboost(self):
        components = CONTROLLER_BUTTON
        if not self.effect:
            components[9].style = ButtonStyle.red
            await self.set_filter(wavelink.Filter(equalizer=wavelink.Equalizer.boost()), seek=True)
            self.effect = True
        else:
            components[9].style = ButtonStyle.gray
            await self.set_filter(wavelink.Filter(), seek=True)
            self.effect = False
        await self.message_controller.edit(components=components)

    async def do_next(self) -> None:
        if self.is_playing() or self.waiting:
            return
        try:
            self.waiting = True
            with async_timeout.timeout(playerSettings['waiting']):
                track = await self.queue.get()
        except asyncio.TimeoutError:
            lang_server = db.get(f"lang_{self.inter.guild.id}") or "ru"
            if lang_server == 'ru':
                return await self.destroy("Очередь пуста")
            if lang_server == 'en':
                return await self.destroy("Queue is empty")
            if lang_server == 'uk':
                return await self.destroy("Черга порожня")

        await self.play(track)
        self.waiting = False
        await self.invoke_controller()

    async def invoke_controller(self):
        qsize = self.queue.qsize()
        components = CONTROLLER_BUTTON
        components[1].custom_id = PlayerControls.PAUSE
        components[1].emoji = emojis['pauseEmoji']

        try:
            message = await self.inter.channel.fetch_message(self.message_controller_id)
            await self.message_controller.edit(embed=self.playerMessage())
            self.message_controller = message
        except:
            if self.inter.channel.id:
                channel = self.bot.get_channel(self.inter.channel.id)
                self.message_controller = await channel.send(embed=self.playerMessage(), components=components)
            else:
                if isinstance(self.inter, disnake.Message):
                    if qsize > 0:
                        self.message_controller = await self.inter.channel.send(embed=self.playerMessage(), components=components)
            self.message_controller_id = self.message_controller.id
        if not self.update_embed.is_running():
            self.update_embed.start()

    async def set_paused(self):
        components = CONTROLLER_BUTTON
        disable_buttons = [0, 2, 3, 4, 5, 6, 7, 8, 9]
        if self.is_paused():
            for button in disable_buttons:
                components[button].disabled = False
            components[1].custom_id = PlayerControls.PAUSE
            components[1].emoji = emojis['pauseEmoji']
            components[1].style = ButtonStyle.gray
            await self.resume()
        else:
            for button in disable_buttons:
                components[button].disabled = True
            components[1].custom_id = PlayerControls.PLAY
            components[1].emoji = emojis['playEmoji']
            components[1].style = ButtonStyle.blurple
            await self.pause()
        await self.message_controller.edit(components=components)

    async def set_loop(self):
        components = CONTROLLER_BUTTON
        components[5].custom_id = PlayerControls.ON_LOOP_MODE if self.loop_mode is True else PlayerControls.LOOP_MODE
        components[5].emoji = emojis['onLoopMode'] if self.loop_mode is True else emojis['loopEmoji']
        components[5].style = ButtonStyle.blurple if self.loop_mode is True else ButtonStyle.gray
        await self.message_controller.edit(components=components)

    async def set_limit(self) -> None:
        components = CONTROLLER_BUTTON
        components[7].custom_id = PlayerControls.VOLUMEP
        components[7].disabled = self.volume == 200
        components[6].custom_id = PlayerControls.VOLUMEM
        components[6].disabled = self.volume == 0
        await self.message_controller.edit(components=components)

    async def add_tracks(self, inter, search: str):
        search = search.strip('<>')
        if not URL_REG.match(search):
            search = f'scsearch:{search}'

        tracks = await self.node.get_tracks(cls=wavelink.SoundCloudTrack, query=search)
        if not tracks:
            lang_server = db.get(f"lang_{self.inter.guild.id}") or "ru"
            if lang_server == 'ru':
                return await inter.send("Не найдено песен по вашему запросу", ephemeral=True)
            if lang_server == 'en':
                return await inter.send("No songs found for your request", ephemeral=True)
            if lang_server == 'uk':
                return await inter.send("Не знайдено пісень на ваш запит", ephemeral=True)

        track = tracks[0]
        track.requester = inter.author if isinstance(inter, disnake.Message) else inter.user
        lang_server = db.get(f"lang_{self.inter.guild.id}") or "ru"
        if lang_server == 'ru':
            embed = disnake.Embed(description=f"Трек под названием **{track.title}** (`{time.strftime('%M:%S', time.gmtime(int(track.length)))}`) был добавлен в очередь", color=0x2b2d31)
        if lang_server == 'en':
            embed = disnake.Embed(description=f"The track called **{track.title}** (`{time.strftime('%M:%S', time.gmtime(int(track.length)))}`) has been added to the queue", color=0x2b2d31)
        if lang_server == 'uk':
            embed = disnake.Embed(description=f"Трек під назвою **{track.title}** (`{time.strftime('%M:%S', time.gmtime(int(track.length)))}`) додано до черги", color=0x2b2d31)
        await inter.send(embed=embed)
        await self.queue.put(track)
        self.inter = inter
        if not self.is_playing():
            await self.do_next()

    @tasks.loop(seconds=playerSettings['playerEditSeconds'])
    async def update_embed(self):
        try:
            await self.message_controller.edit(embed=self.playerMessage())
        except (disnake.NotFound, disnake.Forbidden):
            return

    def playerMessage(self) -> disnake.Embed | None:
        track = self.track
        qsize = self.queue.qsize()
        embed = disnake.Embed(color=0x2b2d31)
        emoji = '🔇' if self.volume == 0 else '🔊'
        text = '⏸️' if self.is_paused() else '▶️'
        self.oh = [track.title for track in self.queue._queue]
        lang_server = db.get(f"lang_{self.inter.guild.id}") or "ru"
        if lang_server == 'ru':
            dur = sum([track.duration for track in self.queue._queue])
            hours, remainder = divmod(dur, 3600)
            durations_track = f"`{int(hours)} ч. {int(time.strftime('%M', time.gmtime(remainder)))} мин.`" if hours else f"`{int(time.strftime('%M', time.gmtime(remainder)))} мин.`"
            embed.set_author(name=f"Запросил {self.inter.author.name}: {track.title}", icon_url=self.inter.author.avatar)
            if qsize == 1:
                text1 = f'В очереди: **{self.oh[0]}** ({durations_track})'
            elif qsize == 2:
                text1 = f'В очереди: **{self.oh[0]}**, и ещё 1 трек ({durations_track})'
            elif qsize >= 3:
                text1 = f'В очереди: **{self.oh[0]}**, и ещё {qsize - 1} трек{"a" if qsize == 3 else "ов"} ({durations_track})'
            else:
                text1 = ''
            self.oh = [track.title for track in self.queue._queue]
            embed.set_footer(text=f"Музыкальный сервер: {self.node.identifier}  -  Нагрузка: {self.node.stats.system_load:.2f}% Подключений: {self.node.stats.playing_players}")
            t_cur = self.position
            t_max = int(track.length)
            ost_time = t_max - t_cur
            odur = time.strftime('%M:%S', time.gmtime(ost_time))
            pos = int(playerSettings['playerProgressCount'] * t_cur / t_max)
            duration = time.strftime('%M:%S', time.gmtime(t_max))
            embed.description = f"\n\n{text} `{time.strftime('%M:%S', time.gmtime(t_cur))} / {duration}` <:1_:1083430189368877168>{TRACK_POSITION_EMBED_EMOJI * pos}" \
                                f"{TRACK_LEFT_EMOJI * (playerSettings['playerProgressCount'] - pos)}<:2_:1083430191944171521> `{odur}` `{emoji} {self.volume}%`\n\n{text1}\n"
        if lang_server == 'en':
            dur = sum([track.duration for track in self.queue._queue])
            hours, remainder = divmod(dur, 3600)
            durations_track = f"`{int(hours)} h. {int(time.strftime('%M', time.gmtime(remainder)))} min.`" if hours else f"`{int(time.strftime('%M', time.gmtime(remainder)))} min.`"
            embed.set_author(name=f"Requested {self.inter.author.name}: {track.title}", icon_url=self.inter.author.avatar)
            if qsize == 1:
                text1 = f'Queue: **{self.oh[0]}** ({durations_track})'
            elif qsize == 2:
                text1 = f'Queue: **{self.oh[0]}**, and 1 more track ({durations_track})'
            elif qsize >= 3:
                text1 = f'Queue: **{self.oh[0]}**, and {qsize - 1} more tracks{"s" if qsize == 3 else "s"} ({durations_track})'
            else:
                text1 = ''
            self.oh = [track.title for track in self.queue._queue]
            embed.set_footer(text=f"Lavalink server: {self.node.identifier}  -  Load CPU: {self.node.stats.system_load:.2f}% Connections: {self.node.stats.playing_players}")
            t_cur = self.position
            t_max = int(track.length)
            ost_time = t_max - t_cur
            odur = time.strftime('%M:%S', time.gmtime(ost_time))
            pos = int(playerSettings['playerProgressCount'] * t_cur / t_max)
            duration = time.strftime('%M:%S', time.gmtime(t_max))
            embed.description = f"\n\n{text} `{time.strftime('%M:%S', time.gmtime(t_cur))} / {duration}` <:1_:1083430189368877168>{TRACK_POSITION_EMBED_EMOJI * pos}" \
                                f"{TRACK_LEFT_EMOJI * (playerSettings['playerProgressCount'] - pos)}<:2_:1083430191944171521> `{odur}` `{emoji} {self.volume}%`\n\n{text1}\n"
        if lang_server == 'uk':
            dur = sum([track.duration for track in self.queue._queue])
            hours, remainder = divmod(dur, 3600)
            durations_track = f"`{int(hours)} ч. {int(time.strftime('%M', time.gmtime(remainder)))} мин.`" if hours else f"`{int(time.strftime('%M', time.gmtime(remainder)))} мин.`"
            embed.set_author(name=f"Запитав {self.inter.author.name}: {track.title}", icon_url=self.inter.author.avatar)
            if qsize == 1:
                text1 = f'В черзі: **{self.oh[0]}** ({durations_track})'
            elif qsize == 2:
                text1 = f'В черзі: **{self.oh[0]}**, та ще 1 трек ({durations_track})'
            elif qsize >= 3:
                text1 = f'В черзі: **{self.oh[0]}**, і ще {qsize - 1} трек{"и" if qsize == 3 else "ів"} ({durations_track})'
            else:
                text1 = ''
            self.oh = [track.title for track in self.queue._queue]
            embed.set_footer(text=f"Музичний сервер: {self.node.identifier}  -  Навантаження: {self.node.stats.system_load:.2f}% Підключень: {self.node.stats.playing_players}")
            t_cur = self.position
            t_max = int(track.length)
            ost_time = t_max - t_cur
            odur = time.strftime('%M:%S', time.gmtime(ost_time))
            pos = int(playerSettings['playerProgressCount'] * t_cur / t_max)
            duration = time.strftime('%M:%S', time.gmtime(t_max))
            embed.description = f"\n\n{text} `{time.strftime('%M:%S', time.gmtime(t_cur))} / {duration}` <:1_:1083430189368877168>{TRACK_POSITION_EMBED_EMOJI * pos}" \
                                f"{TRACK_LEFT_EMOJI * (playerSettings['playerProgressCount'] - pos)}<:2_:1083430191944171521> `{odur}` `{emoji} {self.volume}%`\n\n{text1}\n"
        return embed

def setup(bot):
    bot.add_cog(Player(bot))
