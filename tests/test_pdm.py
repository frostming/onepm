import pytest

from onepm import pa, pi, pr, pu, pun

pytestmark = pytest.mark.usefixtures("pdm")


@pytest.mark.parametrize(
    "args, expected_command",
    [
        ([], "install"),
        (["-d"], "install"),
        (["-Gsecurity"], "install"),
        (["-d", "--group=security", "--foo"], "install"),
        (["--no-sync", "-e", "./foo"], "add"),
        (["-G", "security", "foo"], "add"),
    ],
)
def test_pdm_pi_dispatch(project, execute_command, args, expected_command):
    pi(args)
    execute_command.assert_called_with(
        ["pdm", expected_command, *args], None, exit=True
    )


def test_pdm_pr(project, execute_command):
    pr(["test", "--no-report"])
    execute_command.assert_called_with(
        ["pdm", "run", "test", "--no-report"], None, exit=True
    )


def test_pdm_pu(project, execute_command):
    pu(["-Gtest", "requests"])
    execute_command.assert_called_with(
        ["pdm", "update", "-Gtest", "requests"], None, exit=True
    )


def test_pdm_pun(project, execute_command):
    pun(["-Gtest", "requests"])
    execute_command.assert_called_with(
        ["pdm", "remove", "-Gtest", "requests"], None, exit=True
    )


def test_pdm_pa(project, execute_command):
    pa(["config", "--local", "python.use_venv", "on"])
    execute_command.assert_called_with(
        ["pdm", "config", "--local", "python.use_venv", "on"], None, exit=True
    )
