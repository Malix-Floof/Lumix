from disnake.ui import Button, Select
from disnake import ButtonStyle
from config import emojis
from .classes import *

TRACK_POSITION_EMBED_EMOJI = "<:5_:1083430173900292178>"
TRACK_LEFT_EMOJI = "<:3_:1083430185761783878>"

CONTROLLER_BUTTON = [
    Button(custom_id=PlayerControls.BACK,
           emoji=emojis['backEmoji'],
           style=ButtonStyle.gray),
    Button(custom_id=PlayerControls.PAUSE,
           emoji=emojis['pauseEmoji'],
           style=ButtonStyle.gray),
    Button(custom_id=PlayerControls.SKIP,
           emoji=emojis['skipEmoji'],
           style=ButtonStyle.gray),
    Button(custom_id=PlayerControls.PLAYLIST,
           emoji=emojis['playlistEmoji'],
           style=ButtonStyle.gray),
    Button(custom_id=PlayerControls.VOLUMEP,
           emoji=emojis['volumepEmoji'],
           style=ButtonStyle.gray),
    Button(custom_id=PlayerControls.SHUFFLE,
           emoji=emojis['shuffleEmoji'],
           style=ButtonStyle.gray),
    Button(custom_id=PlayerControls.STOP,
           emoji=emojis['stopEmoji'],
           style=ButtonStyle.gray),
    Button(custom_id=PlayerControls.LOOP_MODE,
           emoji=emojis['loopEmoji'],
           style=ButtonStyle.gray),
    Button(custom_id=PlayerControls.BASSBOOST,
           emoji=emojis['bassboostEmoji'],
           style=ButtonStyle.gray),
    Button(custom_id=PlayerControls.VOLUMEM,
           emoji=emojis['volumemEmoji'],
           style=ButtonStyle.gray),
]
