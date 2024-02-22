from unittest import mock

import pytest

from onepm import pa, pi, pu, pun

pytestmark = pytest.mark.usefixtures("uv")


@pytest.mark.parametrize(
    "args", [[], ["--dry-run"], ["--extra-index-url", "http://example.org"]]
)
def test_uv_pi(project, execute_command, args):
    pi(args)
    execute_command.assert_called_with(
        ["uv", "pip", "sync", *args, "pyproject.toml"], mock.ANY
    )


def test_uv_pu(project, execute_command):
    pu([])
    execute_command.assert_called_with(
        ["uv", "pip", "compile", "-o", "requirements.lock", "pyproject.toml"], mock.ANY
    )


def test_uv_pun(project, execute_command):
    pun(["requests"])
    execute_command.assert_called_with(["uv", "pip", "uninstall", "requests"], mock.ANY)


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
    )
