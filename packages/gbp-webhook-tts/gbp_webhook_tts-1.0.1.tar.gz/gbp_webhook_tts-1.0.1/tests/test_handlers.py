# pylint: disable=missing-docstring
from unittest import TestCase, mock

from unittest_fixtures import Fixtures, given

from gbp_webhook_tts import handlers, utils

from . import fixtures as tf


@given(tf.acquire_sound_file, tf.popen)
class BuildPulledTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        # Given the event
        event = {"name": "build_pulled", "machine": "babette", "data": {}}

        # When build_pulled is called with the event
        handlers.build_pulled(event)

        # Then the sound file for the event is acquired
        acquire_sound_file: mock.Mock = fixtures.acquire_sound_file
        acquire_sound_file.assert_called_once_with(event)

        # And the sound file is played
        player = utils.get_sound_player()
        sound_file = acquire_sound_file.return_value
        popen_cls: mock.Mock = fixtures.popen
        popen_cls.assert_called_once_with([*player, str(sound_file)])
