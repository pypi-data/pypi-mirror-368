"""Handler(s) for gbp-webhook-playsound"""

import subprocess as sp
from typing import Any

from gbp_webhook_playsound import get_sound_file, get_sound_player


def build_pulled(_event: Any) -> None:
    """build_pulled event handler"""
    with sp.Popen([*get_sound_player(), get_sound_file("build_pulled")]):
        pass
