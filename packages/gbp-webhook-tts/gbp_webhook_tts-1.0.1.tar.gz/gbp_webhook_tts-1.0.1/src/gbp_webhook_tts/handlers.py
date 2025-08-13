"""gbp-webhook handler"""

import subprocess as sp
from typing import Any

from . import utils


def build_pulled(event: dict[str, Any]) -> None:
    """build_pulled event handler"""
    with sp.Popen([*utils.get_sound_player(), str(utils.acquire_sound_file(event))]):
        pass
