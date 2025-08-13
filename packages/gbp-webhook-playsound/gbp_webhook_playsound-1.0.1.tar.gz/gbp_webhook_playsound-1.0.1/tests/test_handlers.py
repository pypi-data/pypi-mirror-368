# pylint: disable=missing-docstring
from collections.abc import MutableMapping
from unittest import TestCase

from unittest_fixtures import Fixtures, given

from gbp_webhook_playsound import DEFAULT_SOUND
from gbp_webhook_playsound.handlers import build_pulled

from . import lib


@given(lib.environ, lib.popen)
class BuildPulledTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        build_pulled(None)

        popen = fixtures.popen
        popen.assert_called_once_with(["pw-play", DEFAULT_SOUND])

    def test_custom_player(self, fixtures: Fixtures) -> None:
        environ: MutableMapping[str, str] = fixtures.environ
        environ["GBP_WEBHOOK_PLAYSOUND_PLAYER"] = "mpg123 -q"

        build_pulled(None)

        popen = fixtures.popen
        popen.assert_called_once_with(["mpg123", "-q", DEFAULT_SOUND])
