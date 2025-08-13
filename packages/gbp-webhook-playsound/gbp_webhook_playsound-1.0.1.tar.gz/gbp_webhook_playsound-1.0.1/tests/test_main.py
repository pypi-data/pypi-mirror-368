# pylint: disable=missing-docstring,unused-argument
from collections.abc import MutableMapping
from unittest import TestCase

from unittest_fixtures import Fixtures, given

from gbp_webhook_playsound import DEFAULT_SOUND, get_sound_file

from . import lib


@given(lib.environ)
class GetSoundFileTests(TestCase):
    def test_default(self, fixtures: Fixtures) -> None:
        self.assertEqual(DEFAULT_SOUND, get_sound_file("build_pulled"))

    def test_environment_variable(self, fixtures: Fixtures) -> None:
        environ: MutableMapping[str, str] = fixtures.environ
        environ["GBP_WEBHOOK_PLAYSOUND_BUILD_PULLED"] = "/foo/bar.mp3"

        self.assertEqual("/foo/bar.mp3", get_sound_file("build_pulled"))
