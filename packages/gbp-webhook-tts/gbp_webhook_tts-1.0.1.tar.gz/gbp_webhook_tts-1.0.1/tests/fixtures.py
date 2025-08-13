# pylint: disable=missing-docstring,redefined-outer-name
import os
import tempfile
from collections.abc import Mapping, MutableMapping
from pathlib import Path
from types import ModuleType as Module
from unittest import mock

from unittest_fixtures import FixtureContext, Fixtures, fixture

from gbp_webhook_tts import handlers, utils

FC = FixtureContext
Mock = mock.Mock


@fixture()
def environ(
    _: Fixtures, *, environ: Mapping[str, str] | None = None
) -> FC[MutableMapping[str, str]]:
    environ = environ or {}

    with mock.patch.dict(os.environ, clear=True):
        os.environ.update(environ)
        yield os.environ


@fixture()
def tmpdir(_: Fixtures) -> FC[Path]:
    with tempfile.TemporaryDirectory() as tempdir:
        yield Path(tempdir)


@fixture()
def popen(_: Fixtures, target: Module = handlers.sp) -> FC[Mock]:
    with mock.patch.object(target, "Popen") as mock_obj:
        yield mock_obj


@fixture()
def acquire_sound_file(_: Fixtures, target: Module = handlers.utils) -> FC[Mock]:
    with mock.patch.object(target, "acquire_sound_file") as mock_obj:
        yield mock_obj


@fixture()
def user_cache_path(_: Fixtures, target: Module = utils.platformdirs) -> FC[Mock]:
    with mock.patch.object(target, "user_cache_path") as mock_obj:
        yield mock_obj


@fixture()
def event_to_speech(_: Fixtures, target: Module = utils) -> FC[Mock]:
    with mock.patch.object(target, "event_to_speech") as mock_obj:
        yield mock_obj


@fixture()
def boto3_session(_: Fixtures, target: Module = utils.boto3) -> FC[Mock]:
    with mock.patch.object(target, "Session") as mock_obj:
        yield mock_obj
