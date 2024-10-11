from unittest import mock

import pytest

from onepm import pa, pi, pu, pun

pytestmark = pytest.mark.usefixtures("uv")


@pytest.mark.parametrize(
    "args", [[], ["--no-dev"], ["--extra-index-url", "http://example.org"]]
)
def test_uv_pi_sync(project, execute_command, args):
    pi(args)
    execute_command.assert_called_with(["uv", "sync", *args], mock.ANY, exit=True)


@pytest.mark.parametrize(
    "args",
    [
        ["requests"],
        ["--extra-index-url", "http://example.org", "requests"],
        ["-r", "requirements.txt"],
    ],
)
def test_uv_pi_install(project, execute_command, args):
    pi(args)
    execute_command.assert_called_with(["uv", "add", *args], mock.ANY, exit=True)


def test_uv_pu(project, execute_command):
    pu([])
    execute_command.assert_any_call(["uv", "lock", "--upgrade"], mock.ANY, exit=False)
    execute_command.assert_any_call(["uv", "sync"], mock.ANY, exit=True)


def test_uv_pun(project, execute_command):
    pun(["requests"])
    execute_command.assert_called_with(
        ["uv", "remove", "requests"], mock.ANY, exit=True
    )


def test_uv_pa(project, execute_command):
    pa(["--venv", "--system-site-packages", "--python", "3.7"])
    execute_command.assert_called_with(
        [
            "uv",
            "--venv",
            "--system-site-packages",
            "--python",
            "3.7",
        ],
        mock.ANY,
        exit=True,
    )
