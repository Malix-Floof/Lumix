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

from disnake.ui import Button
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
