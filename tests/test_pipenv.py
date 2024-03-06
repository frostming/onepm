import pytest

from onepm import pa, pi, pr, pu, pun

pytestmark = pytest.mark.usefixtures("pipenv")


@pytest.mark.parametrize("args", [[], ["--dev"], ["--keep-outdated", "requests"]])
def test_pipenv_pi(project, execute_command, args):
    pi(args)
    execute_command.assert_called_with(["pipenv", "install", *args], None, exit=True)


def test_pipenv_pr(project, execute_command):
    pr(["test", "--no-report"])
    execute_command.assert_called_with(
        ["pipenv", "run", "test", "--no-report"], None, exit=True
    )


def test_pipenv_pu(project, execute_command):
    pu(["requests"])
    execute_command.assert_called_with(
        ["pipenv", "update", "requests"], None, exit=True
    )


def test_pipenv_pun(project, execute_command):
    pun(["-d", "requests"])
    execute_command.assert_called_with(
        ["pipenv", "uninstall", "-d", "requests"], None, exit=True
    )


def test_pipenv_pa(project, execute_command):
    pa(["--venv", "--system-site-packages", "--python", "3.7"])
    execute_command.assert_called_with(
        [
            "pipenv",
            "--venv",
            "--system-site-packages",
            "--python",
            "3.7",
        ],
        None,
        exit=True,
    )
