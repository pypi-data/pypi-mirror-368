# pylint: disable=missing-docstring,redefined-outer-name
import os
import subprocess
from collections.abc import Mapping, MutableMapping
from unittest import mock

from unittest_fixtures import FixtureContext, Fixtures, fixture


@fixture()
def environ(
    _fixtures: Fixtures, *, environ: Mapping[str, str] | None = None, clear: bool = True
) -> FixtureContext[MutableMapping[str, str]]:
    with mock.patch.dict(os.environ, clear=clear):
        os.environ.update(environ or {})
        yield os.environ


@fixture()
def popen(_fixtures: Fixtures) -> FixtureContext[mock.Mock]:
    with mock.patch.object(subprocess, "Popen") as mock_popen:
        yield mock_popen
