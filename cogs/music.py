from random import shuffle
import disnake.errors
from utils import *
import lumix.print
from db import SQLITE

db = SQLITE("database.db")


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_timer = {}
        self.user_all_time = {}
        self.queue = asyncio.Queue()
        self.oh = None
        self.effect = False

    async def cog_slash_command_error(self, inter, error):
        await super().cog_slash_command_error(inter, error)
        raise error

    @commands.Cog.listener("on_button_click")
    @commands.Cog.listener("on_component")
    async def interaction(self, inter):
        if not inter.data.custom_id.startswith("musicplayer_"):
            return

        await self.player_controller(inter, inter.data.custom_id)

    @commands.Cog.listener()
    async def on_ready(self):
        await lumix.print.log(f"music.py is ready")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        lang_server = db.get(f"lang_{member.guild.id}") or "ru"
        """stats = {
            'ru': {
                'destroy': 'Я была отключена от голосового канала',
                'move': 'Я была перемещена в другой канал',
                'empty': 'В голосовом канале не осталось участников'
            },
            'en': {
                'destroy': 'I was disconnected from the voice channel',
                'move': 'I have been moved to another channel', 
                'empty': 'There are no members left in the voice channel'
            },
            'uk': {
                'destroy': 'Я була відключена від голосового каналу',
                'move': 'Я була переміщена в інший канал', 
                'empty': 'У голосовому каналі не залишилося учасників'
            }
        }"""

        player = self.bot.node.get_player(member.guild)

        if before.channel == after.channel or not player:
            return

        if before.channel is not None and after.channel is not None:
            if lang_server == 'ru':
                return await player.destroy("Я была перемещена в другой канал")
            if lang_server == 'en':
                return await player.destroy("I have been moved to another channel")
            if lang_server == 'uk':
                return await player.destroy("Я була переміщена в інший канал")
            
        if member.id == self.bot.user.id and after.channel is None:
            if lang_server == 'ru':
                await player.destroy("Я была отключена от голосового канала")
            if lang_server == 'en':
                await player.destroy("I was disconnected from the voice channel")
            if lang_server == 'uk':
                await player.destroy("Я була відключена від голосового каналу")

        if not any(not member.bot for member in player.channel.members):
            if lang_server == 'ru':
                await player.destroy("В голосовом канале не осталось участников")
            if lang_server == 'en':
                await player.destroy("There are no members left in the voice channel")
            if lang_server == 'uk':
                await player.destroy("У голосовому каналі не залишилося учасників")
                

    @commands.Cog.listener("on_wavelink_track_exception")
    @commands.Cog.listener("on_wavelink_track_end")
    @commands.Cog.listener("on_wavelink_track_stuck")
    async def on_player_stop(self, player, *args, **kwargs):
        if player.loop_mode:
            await player.play(player.looped_track)
            return
        player.update_embed.cancel()
        await player.do_next()

    async def player_controller(self, inter, control: str):
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        player = self.bot.node.get_player(inter.guild)
        if player:
            match control:
                case PlayerControls.BACK:
                    await player.seek(0)
                    if lang_server == 'ru':
                        await inter.send(f"Трек перемотан на начало", ephemeral=True)
                    if lang_server == 'en':
                        await inter.send(f"Track rewound to the beginning", ephemeral=True)
                    if lang_server == 'uk':
                        await inter.send(f"Трек перемотаний на початок", ephemeral=True)
                case PlayerControls.PLAY:
                    await player.set_paused()
                    if lang_server == 'ru':
                        await inter.send(f"{inter.author.name} снял трек с паузы")
                    if lang_server == 'en':
                        await inter.send(f"{inter.author.name} unpaused the track")
                    if lang_server == 'uk':
                        await inter.send(f"{inter.author.name} зняв трек із паузи")
                case PlayerControls.SKIP:
                    if lang_server == 'ru':
                        await inter.send(f'{inter.author.name} пропустил трек "`{player.track.title}`"')
                    if lang_server == 'en':
                        await inter.send(f'{inter.author.name} missed a track "`{player.track.title}`"')
                    if lang_server == 'uk':
                        await inter.send(f'{inter.author.name} пропустив трек "`{player.track.title}`"')
                    await player.stop()
                case PlayerControls.PAUSE:
                    await player.set_paused()
                    if lang_server == 'ru': 
                        await inter.send(f"{inter.author.name} поставил трек на паузу")
                    if lang_server == 'en':
                        await inter.send(f"{inter.author.name} pause the track")
                    if lang_server == 'uk':
                        await inter.send(f"{inter.author.name} поставив трек на паузу")
                case PlayerControls.STOP:
                    if lang_server == 'ru':
                        await player.destroy(f"Плеер был остановлен: {inter.author.name}")
                    if lang_server == 'en':
                        await player.destroy(f"The player has been stopped: {inter.author.name}")
                    if lang_server == 'uk':
                        await player.destroy(f"Плеєр було зупинено: {inter.author.name}")
                case PlayerControls.SHUFFLE:
                    if player.queue.qsize() < 3:
                        if lang_server == 'ru':
                            return await inter.send("Мало треков в очереди! Требуется как минимум 3", ephemeral=True)
                        if lang_server == 'en':
                            return await inter.send("Few tracks in the queue! Requires at least 3", ephemeral=True)
                        if lang_server == 'uk':
                            return await inter.send("Мало треків у черзі! Потрібно як мінімум 3", ephemeral=True)
                    shuffle(player.queue._queue)
                    if lang_server == 'ru':
                        await inter.send("Очередь была перемешана", ephemeral=True)
                    if lang_server == 'en':
                        await inter.send("The queue has been jumbled", ephemeral=True)
                    if lang_server == 'uk':
                        await inter.send("Черга була перемішана", ephemeral=True)
                case PlayerControls.LOOP_MODE:
                    player.looped_track = player.track
                    player.loop_mode = True
                    await player.set_loop()
                    if lang_server == 'ru':
                        await inter.send(f"Повтор трека был включен", ephemeral=True)
                    if lang_server == 'en':
                        await inter.send(f"Track repeat turned on", ephemeral=True)
                    if lang_server == 'uk':
                        await inter.send(f"Повторення треку було включено", ephemeral=True)
                case PlayerControls.ON_LOOP_MODE:
                    player.loop_mode = False
                    await player.set_loop()
                    if lang_server == 'ru':
                        await inter.send(f"Повтор трека был выключен", ephemeral=True)
                    if lang_server == 'en':
                        await inter.send(f"Track repeat has been turned off", ephemeral=True)
                    if lang_server == 'uk':
                        await inter.send(f"Повторення треку було вимкнено", ephemeral=True)
                case PlayerControls.VOLUMEM:
                    volume = player.volume
                    await player.set_volume(volume - 10)
                    await player.set_limit()
                    if lang_server == 'ru':
                        await inter.send(f"Громкость снижена на 10%, текущая громкость: {player.volume}%", ephemeral=True)
                    if lang_server == 'en':
                        await inter.send(f"Volume reduced by 10%, current volume: {player.volume}%", ephemeral=True)
                    if lang_server == 'uk':
                        await inter.send(f"Гучність знижена на 10%, поточна гучність: {player.volume}%", ephemeral=True)
                case PlayerControls.VOLUMEP:
                    volume = player.volume
                    await player.set_volume(volume + 10)
                    await player.set_limit()
                    if lang_server == 'ru':
                        await inter.send(f"Громкость увеличена на 10%, текущая громкость: {player.volume}%", ephemeral=True)
                    if lang_server == 'en':
                        await inter.send(f"Volume increased by 10%, current volume: {player.volume}%", ephemeral=True)
                    if lang_server == 'uk':
                        await inter.send(f"Гучність збільшена на 10%, поточна гучність: {player.volume}%", ephemeral=True)
                case PlayerControls.PLAYLIST:
                    duration = sum([track.duration for track in player.queue._queue])
                    current_track = player.current
                    qsize = player.queue.qsize()
                    self.oh = [track.title for track in player.queue._queue]
                    if current_track:
                        self.queue._queue.remove(current_track)
                    queue = '\n'.join([f"{i + 1}. `{time.strftime('%M:%S', time.gmtime(track.duration))}` - {track.title}" for i, track in enumerate(player.queue._queue)])
                    embed = disnake.Embed(color=0x2b2d31)
                    if player.queue.qsize() == 0:
                        if lang_server == 'ru':
                            title = ' '.join(['Очередь сервера отсутствует'])
                        if lang_server == 'en':
                            title = ' '.join(['Server queue missing'])
                        if lang_server == 'uk':
                            title = ' '.join(['Черга сервера відсутня'])
                        embed.title = title
                        embed.set_footer(text=" ")
                    elif player.queue.qsize() > 0:
                        if lang_server == 'ru':
                            title = ' '.join(['Очередь сервера'])
                        if lang_server == 'en':
                            title = ' '.join(['Server Queue'])
                        if lang_server == 'uk':
                            title = ' '.join(['Черга сервера'])
                        embed.title = title
                        if qsize == 1:
                            if lang_server == 'ru':
                                text1 = f'В очереди: {qsize} трек'
                            if lang_server == 'en':
                                text1 = f'In queue: {qsize} track'
                            if lang_server == 'uk':
                                text1 = f'У черзі: {qsize} трек'
                        elif 2 <= qsize <= 4:
                            if lang_server == 'ru':
                                text1 = f'В очереди: {qsize} трека'
                            if lang_server == 'en':
                               text1 = f'In queue: {qsize} tracks'
                            if lang_server == 'uk':
                                text1 = f'У черзі: {qsize} треку'
                        elif qsize > 4:
                            if lang_server == 'ru':
                                text1 = f'В очереди: {qsize} треков'
                            if lang_server == 'en':
                                text1 = f'In queue: {qsize} tracks'
                            if lang_server == 'uk':
                                text1 = f'У черзі: {qsize} треків'

                        embed.set_footer(text=f"{text1}", icon_url=inter.user.avatar)
                    hours, remainder = divmod(duration, 3600)
                    if hours == 0:
                        if lang_server == 'ru':
                            duration = f"`{int(time.strftime('%M', time.gmtime(remainder)))} мин.`"
                        if lang_server == 'en':
                            duration = f"`{int(time.strftime('%M', time.gmtime(remainder)))} min.`"
                        if lang_server == 'uk':
                            duration = f"`{int(time.strftime('%M', time.gmtime(remainder)))} хв.`"
                    else:
                        if lang_server == 'ru':
                            duration = f"`{int(hours)} ч. {int(time.strftime('%M', time.gmtime(remainder)))} мин.`"
                        if lang_server == 'en':
                            duration = f"`{int(hours)} h. {int(time.strftime('%M', time.gmtime(remainder)))} min.`"
                        if lang_server == 'uk':
                            duration = f"`{int(hours)} год. {int(time.strftime('%M', time.gmtime(remainder)))} хв.`"
                    if lang_server == 'ru':
                        embed.description = f"{qsize} трек(-ов), примерное время {duration} \n\n{queue}"
                    if lang_server == 'en':
                        embed.description = f"{qsize} track(s), estimated time {duration} \n\n{queue}"
                    if lang_server == 'uk':
                        embed.description = f"{qsize} трек(-ів), зразковий час {duration} \n\n{queue}"
                    await inter.send(embed=embed, ephemeral=True)
                case PlayerControls.BASSBOOST:
                    await player.bassboost()
                    if player.effect is False:
                        if lang_server == 'ru':
                            await inter.send("Установлен фильтр 'Обычный'", ephemeral=True)
                        if lang_server == 'en':
                            await inter.send("Set filter 'Default'", ephemeral=True)
                        if lang_server == 'uk':
                            await inter.send("Встановлено фільтр 'Звичайний'", ephemeral=True)
                    if player.effect is True:
                        if lang_server == 'ru':
                            await inter.send("Установлен фильтр 'Бас буст'", ephemeral=True)
                        if lang_server == 'en':
                            await inter.send("Set filter 'Bass Boost'", ephemeral=True)
                        if lang_server == 'uk':
                            await inter.send("Встановлено фільтр 'Бас буст'", ephemeral=True)

    async def connect(self, inter, user, channel=None):
        player = Player(inter=inter, bot=self.bot)
        voice_channel = getattr(user.voice, 'channel', channel)
        await voice_channel.connect(cls=player)
        await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)
        return player

    @commands.slash_command(description="🎶 Музыка | Воспроизвести музыку в голосовом канале")
    async def play(self, inter, search: str = commands.Param(name="название", description="название трека")):
        if not inter.author.voice:
            return await inter.send("Вы должны присоединиться к голосовому каналу, чтобы начать прослушивание музыки!", ephemeral=True)

        player = self.bot.node.get_player(inter.guild)
        service_blacklist = ["www.youtube.com", "youtu.be", "twitch.tv"]
        if any(service in search for service in service_blacklist):
            await inter.send("Данный сервис не поддерживается, используйте другой!", ephemeral=True)
            return

        if player is None or not player.is_connected():
            player = await self.connect(inter, inter.user)

        voice_state = inter.author.voice.channel.id
        voice_client = inter.guild.voice_client.channel.id
        if voice_state is None:
            await inter.send("Вы должны присоединиться к голосовому каналу, чтобы начать прослушивание музыки!",
                             ephemeral=True)
            return
        if voice_state != voice_client:
            return await inter.send(
                f"Я уже играю музыку в канале {voice_client.channel.mention}, присоединитесь к этому каналу, чтобы получить доступ для управления плеером",
                ephemeral=True)

        await player.add_tracks(inter, search)

    @commands.slash_command(description="🎶 Музыка | Остановить плеер")
    async def stop(self, inter):
        player = self.bot.node.get_player(inter.guild.id)
        if not player or not player.is_playing():
            return await inter.send("Музыка сейчас не играет", ephemeral=True)
        if not inter.author.voice or not inter.author.voice.channel:
            return await inter.send("Вы должны находиться в голосовом канале, чтобы использовать эту команду!", ephemeral=True)
        await player.destroy(f"Плеер был остановлен: {inter.author.name}")

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    @commands.slash_command(description="🎶 Музыка | Настройка громкости")
    async def volume(self, inter, volume: commands.Range[int, 0, 200] = commands.Param(
                name="громкость",
                description="Вы можете установить громкость в диапозоне от 0 до 200"
    )):
        await inter.response.defer()
        lang_server = db.get(f"lang_{inter.guild.id}") or "ru"
        player = self.bot.node.get_player(inter.guild)
        if not player or not player.is_playing():
            if lang_server == 'ru':
                return await inter.send(f"Музыка сейчас не играет", ephemeral=True)
            if lang_server == 'en':
                return await inter.send(f"Music is not playing now", ephemeral=True)
            if lang_server == 'uk':
                return await inter.send(f"Музика зараз не грає", ephemeral=True)
        if inter.author.voice is None or inter.author.voice.channel is None:
            if lang_server == 'ru':
                return await inter.send(f"Вы должны находиться в голосовом канале что бы использовать эту команду!", ephemeral=True)
            if lang_server == 'en':
                return await inter.send(f"You must be in a voice channel to use this command!", ephemeral=True)
            if lang_server == 'us':
                return await inter.send(f"Ви повинні знаходитися в голосовому каналі, щоб використовувати цю команду!", ephemeral=True)
        await player.set_volume(volume)
        await player.set_limit()
        if lang_server == 'ru':
            await inter.send(f"Громкость плеера установлена на {volume}%", ephemeral=True)
        if lang_server == 'en':
            await inter.send(f"Player volume set to {volume}%", ephemeral=True)
        if lang_server == 'us':
            await inter.send(f"Гучність плеєра встановлена ​​на {volume}%", ephemeral=True)


def setup(bot):
    bot.add_cog(Music(bot))
