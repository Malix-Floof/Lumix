import time
import mafic
import asyncio
import aiohttp
import disnake

from disnake.ext import commands
from config import emojis, lavalink
from random import shuffle
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


class PageModal(disnake.ui.Modal):
    def __init__(self):
        super().__init__(
            title="Перейти к странице", 
            custom_id="page_modal",
            timeout=300,
            components=[
                disnake.ui.TextInput(
                    label="Страница", 
                    placeholder="Укажите номер страницы", 
                    custom_id="page_num", 
                    style=disnake.TextInputStyle.short, 
                    max_length=3
                ),
            ],
        )

    async def callback(self, interaction) -> None:
        player = interaction.guild.voice_client
        try:
            paginator = Paginator(
                target_page=int(dict(interaction.text_values.items()).get('page_num')), 
                embeds=player.pages
            )
            await paginator.start(
                interaction,
                deferred=True
            )
        except IndexError:
            await interaction.send(
                f"Страница не сущевствует! Укажите число в диапазоне от 1 до {len(player.pages)}", 
                ephemeral=True
            )


class Paginator:
    def __init__(
            self, 
            embeds,
            target_page=1, 
            timeout=300, 
            back="◀️",
            next="▶️",
            button_style=disnake.ButtonStyle.gray, 
        ):
        self.embeds = embeds
        self.current_page = target_page if 1 <= target_page <= len(embeds) else 1
        self.timeout = timeout
        self.back = back
        self.next = next
        self.button_style = button_style

        class PaginatorView(disnake.ui.View):
            def __init__(this, interaction):
                super().__init__(timeout=self.timeout)
                this.interaction = interaction

            async def on_timeout(this):
                for button in this.children:
                    button.disabled = True
                await this.interaction.edit_original_message(embed=self.embeds[self.current_page-1], view=this)
                return await super().on_timeout()

            @disnake.ui.button(emoji=self.back, style=self.button_style, disabled=len(self.embeds) == 1)
            async def previous_button(this, _, button_interaction):
                self.current_page = (self.current_page - 2) % len(self.embeds) + 1
                await button_interaction.response.edit_message(embed=self.embeds[self.current_page-1], view=this)

            @disnake.ui.button(label=f"Перейти к странице", style=self.button_style, disabled=len(self.embeds) == 1)
            async def page_button(this, _, button_interaction):
                await button_interaction.response.send_modal(PageModal())

            @disnake.ui.button(emoji=self.next, style=self.button_style, disabled=len(self.embeds) == 1)
            async def next_button(this, _, button_interaction):
                self.current_page = self.current_page % len(self.embeds) + 1
                await button_interaction.response.edit_message(embed=self.embeds[self.current_page-1], view=this)

        self.view = PaginatorView

    async def start(self, interaction, ephemeral=False, deferred=False):
        if not deferred:
            await interaction.response.send_message(
                embed=self.embeds[self.current_page-1], 
                view=self.view(interaction), 
                ephemeral=ephemeral
            )
        else:
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page-1], 
                view=self.view(interaction)
            )


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
        self.effect: bool = False

    async def queue_type(self, value):
        self.loop_mode = value
        self.is_looping = value in ('track', 'queue')


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def destroy(self, player: Player):
        if player.controller is None:
            await player.destroy()
            return
        
        if not player.queue:
            await player.controller.edit(view=None)
            return await player.destroy()

        if player.loop_mode == 'track':
            await player.play(player.queue[0])
            return

        if player.loop_mode == 'queue':
            player.index = (player.index + 1) % len(player.queue)
            await player.play(player.queue[player.index])
            return

        player.queue.pop(0)
        if player.queue:
            await player.play(player.queue[0])
            return
    
        await player.controller.edit(view=None)
        await player.destroy()
    
    @commands.Cog.listener("on_track_exception")
    @commands.Cog.listener("on_track_end")
    async def сonditions(self, event):
        await self.destroy(event.player)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        player = member.guild.voice_client
        if not player:
            return

        elif not any(not member.bot for member in player.channel.members):
            player.queue.clear()
            await self.destroy(player)
            return

        elif member.id == self.bot.user.id and after.channel is None:
            player.queue.clear()
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

                if int(dj) in player.djs:
                    player.djs.pop(int(dj))
                    await inter.followup.send(f"<@{inter.data.values[0]}> Был убран из списка диджеев!", delete_after=5)
                else:
                    player.djs.append(int(dj))
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
                disable_buttons = [1, 3, 4, 5, 6, 7, 8, 9, 10]
                if player.paused:
                    for button in disable_buttons:
                        view.children[button].disabled = False
                    view.children[2].emoji = emojis['pauseEmoji']
                    view.children[2].style = disnake.ButtonStyle.gray
                    await player.resume()
                    self.update_embed(player)
                else:
                    for button in disable_buttons:
                        view.children[button].disabled = True
                    view.children[2].emoji = emojis['playEmoji']
                    view.children[2].style = disnake.ButtonStyle.blurple
                    await player.pause()

                if player.is_looping:
                    view.children[8].emoji = emojis['onLoopMode']
                    view.children[8].style = disnake.ButtonStyle.blurple

                if player.effect is True:
                    view.children[9].style = disnake.ButtonStyle.red

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

            paginator = Paginator(embeds=player.pages)
            await paginator.start(inter, ephemeral=True)

        if inter.data['custom_id'] == 'volumep:5':
            if await self.cheks(inter, player):
                player.volume += 10
                await player.set_volume(player.volume)
                await self.volume_blocked(player)
                if player.is_looping:
                    view.children[8].emoji = emojis['onLoopMode']
                    view.children[8].style = disnake.ButtonStyle.blurple
                if player.effect:
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
                player.queue.clear()
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
                if player.effect:
                    view.children[9].style = disnake.ButtonStyle.red

                return await player.controller.edit(view=view)


        if inter.data['custom_id'] == 'bassboost:9':
            if await self.cheks(inter, player):
                if player.effect is False:
                    view.children[9].style = disnake.ButtonStyle.red
                    player.effect = True
                    await player.add_filter(mafic.Filter(karaoke=mafic.Karaoke(3, 3)), label="karaoke", fast_apply=True)
                    if player.is_looping:
                        view.children[8].emoji = emojis['onLoopMode']
                        view.children[8].style = disnake.ButtonStyle.blurple
                    await player.controller.edit(view=view)
                    return

                if player.effect:
                    view.children[9].style = disnake.ButtonStyle.gray
                    await player.clear_filters(fast_apply=True)
                    player.effect = False
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
                if player.effect:
                    view.children[9].style = disnake.ButtonStyle.red
                await player.controller.edit(embed=await self.playerMessage(player))

                
    @commands.slash_command(
        description="🎶 Воспроизвести музыку в голосовом канале",
        dm_permission=False
    )
    async def play(
        self,
        inter: disnake.AppCmdInter,
        search: str = commands.Param(
            name="название",
            description="название трека"
        )
    ) -> None:
        await inter.response.defer()
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        try:
            if not inter.author.voice:
                return await inter.edit_original_response("Вы должны присоединиться к голосовому каналу, чтобы начать прослушивание музыки!")
            if not inter.guild.voice_client:
                player = await inter.user.voice.channel.connect(cls=Player)
            else:
                player: Player = inter.guild.voice_client

            service_blacklist = ["www.youtube.com", "youtu.be", "twitch.tv"]
            if any(service in search for service in service_blacklist):
                return await inter.edit_original_response("Данный сервис не поддерживается, используйте другой!")

            voice_state = inter.author.voice.channel.id
            voice_channel = getattr(inter.user.voice, 'channel', inter.guild.voice_client)
            await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)

            if inter.guild.voice_client:
                voice_client = inter.guild.voice_client.channel.id
                if voice_state != voice_client:
                    await inter.send(
                        f"Я уже играю музыку в канале {inter.guild.voice_client.channel.mention}!",
                    )
                    return

            tracks = await player.fetch_tracks(search, mafic.SearchType.SOUNDCLOUD)
            if not tracks:
                return await inter.edit_original_response("Трек по вашему запросу не найден")

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
                    return await inter.send(embed=embed, delete_after=5)
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
        
        except mafic.NoNodesAvailable as e:
            message = {
                'ru': 'Ой ой! Кажется, нет доступных музыкальных серверов, повторите попытку позже или обратитесь на сервер поддержки!',
                'en': 'Oh! There don\'t seem to be any music servers available, try again later or contact the support server!',
                'uk': 'Ой ой! Здається, немає доступних музичних серверів, спробуйте пізніше або зверніться до сервера підтримки!'
            }[lang_server]
            await inter.edit_original_response(message)
            
        except Exception as e:
            print(e)
            message = {
                'ru': 'Неизвестный формат трека. Пожалуйста, предоставьте ссылку на трек в Soundcloud или введите название трека',
                'en': 'Unknown track format. Please provide a link to the track on Soundcloud or enter the track name',
                'uk': 'Невідомий формат треку. Будь ласка, надайте посилання на трек у Soundcloud або введіть назву треку'
            }[lang_server]
            await inter.edit_original_response(message)

    async def search(self, query, searchtype = 'scsearch') -> None:
        url = f"http://{lavalink['host']}:{lavalink['port']}/v4/loadtracks"
        params = {'identifier': f'{searchtype}:{query}'}
        headers = {
            'Authorization': lavalink['password'],
            'Accept': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                tracks = []
                if response.status == 200:
                    data = await response.json()
                    for item in data['data']:
                        tracks.append(disnake.OptionChoice(name=f"{item['info']['title']}", value=item['info']['uri'][:100]))

                return tracks
            
    @play.autocomplete("название")
    async def autoplay(self, inter: disnake.AppCmdInter, string: str):
        if not string:
            return []
            
        return await self.search(string)

    @commands.slash_command(description="🎶 Остановить плеер")
    async def stop(self, inter: disnake.AppCmdInter) -> None:
        await inter.response.defer()
        player = inter.guild.voice_client
        if not player:
            return await inter.send("Музыка сейчас не играет", ephemeral=True)
        
        await self.destroy(player)
        await inter.send("Плеер был остановлен")

    @commands.slash_command(description="🎶 Настройка громкости")
    async def volume(
        self, inter: disnake.AppCmdInter, 
        volume: commands.Range[int, 0, 200] = commands.Param(
            name="громкость",
            description="Вы можете установить громкость в диапозоне от 0 до 200"
    )) -> None:
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
                ...
            await asyncio.sleep(6)
            
    async def ftrk(self, n: int) -> str:
        if n % 10 == 1 and n % 100 != 11:
            return f"{n} трек"
        elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
            return f"{n} трека"
        else:
            return f"{n} треков"

    async def playerMessage(self, player):
        lang_server = db.get(f"lang_{player.guild.id}") or "ru"
        track = player.current
        volume = player.volume
        qsize = len(player.queue)
        embed = disnake.Embed(color=0x2b2d31)
        embed.set_thumbnail(url=track.artwork_url)
        emoji = '🔇' if volume == 0 else '🔊'
        text = '⏸️' if player.paused else '▶️'
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
            days, remainder = divmod(dur, 86400)
            hours, remainder = divmod(dur, 3600)
            minutes = int(time.strftime('%M', time.gmtime(remainder)))
            odur = f"`{time.strftime('%M:%S', time.gmtime(ost_time))}`"
            duration = time.strftime('%M:%S', time.gmtime(t_max))
            timed = f"{time.strftime('%M:%S', time.gmtime(t_cur))} / {duration}"
            if ost_time < 4:
                positionbar = f"<:1_:1083430189368877168>{posEmoji * 7}<:224:1160530351505035357>"
            else:
                positionbar = f"<:1_:1083430189368877168>{posEmoji * pos}{leftEmoji * (7 - pos)}<:2_:1083430191944171521>"

        if lang_server == 'ru':
            days = dur // (24 * 3600)
            hours = (dur % (24 * 3600)) // 3600
            minutes = (dur % 3600) // 60
            durations_track = ""
            if days > 0:
                durations_track += f"{int(days)} дн. "
            if hours > 0:
                durations_track += f"{int(hours)} ч. "
            if minutes > 0:
                durations_track += f"{int(minutes)} мин."
                
            embed.set_author(
                name=f"Сейчас играет: {player.current.title}",
                icon_url=searchtype,
                url=track.uri,
            )
            text1 = '**✨ В очереди пусто! Добавьте что нибудь 🎵**'
            if qsize == 2:
                text1 = f'В очереди: **{player.queue[1].title}** (`~ {durations_track}`)'
            elif qsize >= 3:
                ftracks = await self.ftrk(len(player.queue) - 2)
                skipTrack = player.queue[1].title[:10]
                text1 = f'В очереди: **{skipTrack if len(skipTrack) <= 10 else f"{skipTrack}..."}** и ещё {ftracks} (`~ {durations_track}`)'

            embed.set_footer(
               text=f"Музыкальный сервер: Tyad "
                    f" -  Нагрузка: {int(player.node.stats.cpu.system_load)}%  - "
                    f" Подключений: {player.node.stats.playing_player_count}"
            )
            embed.description = f"\n\n{text} `{timed}` {positionbar} {odur} `{emoji} {volume}%` \n\n{text1}\n"
            embed.description = embed.description[:2048]
        if lang_server == 'en':
            durations_track = f"{int(hours)} h. {int(time.strftime('%M', time.gmtime(remainder)))} min.`" if hours else f"`{int(time.strftime('%M', time.gmtime(remainder)))} min."
            embed.set_author(
                name=f"Now playing: {player.current.title}",
                icon_url=searchtype,
                url=track.uri,
            )
            text1 = '**✨ The queue is empty! Add something 🎵**'
            if qsize == 2:
                text1 = f'Queue: **{player.queue[1].title}** (`~ {durations_track}`)'
            elif qsize == 3:
                text1 = f'Queue: **{player.queue[1].title}**, and 2 more track (`~ {durations_track}`)'
            elif qsize >= 4:
                text1 = f'Queue: **{player.queue[1].title}**, and {qsize - 1} more tracks{"s" if qsize == 3 else "s"} (`~ {durations_track}`)'

            embed.set_footer(
                text=f"Lavalink server: Tyad "
                     f" Connections:  {player.node.stats.playing_player_count}"
            )
            embed.description = f"\n\n{text} `{timed}` {positionbar} `{odur}` `{emoji} {volume}%` \n\n{text1}\n"
        if lang_server == 'uk':
            durations_track = f"{int(hours)} ч. {int(time.strftime('%M', time.gmtime(remainder)))} мин.`" if hours else f"`{int(time.strftime('%M', time.gmtime(remainder)))} мин."
            embed.set_author(
                name=f"Зараз грає: {player.current.title}",
                icon_url=searchtype,
                url=track.uri,
            )
            text1 = '**✨ Черга порожня! Додайте що-небудь 🎵**'
            if qsize == 2:
                text1 = f'В черзі: **{player.queue[1].title}** (`~ {durations_track}`)'
            elif qsize == 3:
                text1 = f'В черзі: **{player.queue[1].title}**, та ще 1 трек (`~ {durations_track}`)'
            elif qsize >= 4:
                text1 = f'В черзі: **{player.queue[1].title}**, і ще {qsize - 1} трек{"и" if qsize == 3 else "ів"} (`~ {durations_track}`)'

            embed.set_footer(
                text=f"Музичний сервер: Tyad "
                     f"Підключень:  {player.node.stats.playing_player_count}"
            )
            embed.description = f"\n\n{text} `{timed}` {positionbar} `{odur}` `{emoji} {volume}%` \n\n{text1}\n"
        return embed


def setup(bot):
    bot.add_cog(Music(bot))
