"""gbp-webhook-tts utils"""

import os
from pathlib import Path
from typing import Any

import boto3
import platformdirs

from gbp_webhook_tts.templates import load_template, render_template

environ = os.environ


def acquire_sound_file(event: dict[str, Any]) -> Path:
    """Acquire the audio file needed for the event and return the path"""
    path: Path = event_to_path(event)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(event_to_speech(event))
    return path


def event_to_path(event: dict[str, Any]) -> Path:
    """Given the path return the pathname of the audio file"""
    machine = event["machine"]

    return platformdirs.user_cache_path("gbp-webhook") / "tts" / f"{machine}.mp3"


def event_to_speech(event: dict[str, Any]) -> bytes:
    """Return .mp3 audio for the given event"""
    text = get_speech_text_for_machine(event["machine"])
    polly = boto3.Session().client("polly")
    response = polly.synthesize_speech(
        VoiceId="Ivy", OutputFormat="mp3", Text=text, TextType="ssml"
    )

    return response["AudioStream"].read()


def get_speech_text_for_machine(machine: str) -> str:
    """Given the machine name, return the text for speech"""
    context = {
        "machine": map_machine_to_text(machine) or machine.replace("-", " "),
        "delay": environ.get("GBP_WEBHOOK_TTS_DELAY", "0"),
    }
    return render_template(load_template("build_pulled.ssml"), context)


def map_machine_to_text(machine: str) -> str | None:
    """Return the phonetic pronunciation for machine if defined

    For example if the machine is "kde-desktop", will return the value of the
    environment variable `GBP_WEBHOOK_TTS_PHONETIC_KDE_DESKTOP`
    """
    return environ.get(f"GBP_WEBHOOK_TTS_PHONETIC_{machine.replace('-', '_').upper()}")


def get_sound_player() -> list[str]:
    """Return the sound player executable"""
    return os.environ.get("GBP_WEBHOOK_PLAYSOUND_PLAYER", "pw-play").split()
