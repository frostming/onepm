import pytest

from onepm import pa, pi, pr, pu, pun

pytestmark = pytest.mark.usefixtures("poetry")


@pytest.mark.parametrize(
    "args, expected_command",
    [
        ([], "install"),
        (["-E", "foo", "-E", "bar"], "install"),
        (["--extras=foo", "--extras=bar"], "install"),
        (["-D", "requests"], "add"),
        (["-D", "-E", "foo", "-E", "bar", "requests"], "add"),
    ],
)
def test_poetry_pi_dispatch(project, execute_command, args, expected_command):
    pi(args)
    execute_command.assert_called_with(
        ["poetry", expected_command, *args], None, exit=True
    )


def test_poetry_pu(project, execute_command):
    pu(["requests"])
    execute_command.assert_called_with(
        ["poetry", "update", "requests"], None, exit=True
    )


def test_poetry_pun(project, execute_command):
    pun(["requests"])
    execute_command.assert_called_with(
        ["poetry", "remove", "requests"], None, exit=True
    )


def test_poetry_pr(project, execute_command):
    pr(["test", "--no-report"])
    execute_command.assert_called_with(
        ["poetry", "run", "test", "--no-report"], None, exit=True
    )


def test_poetry_pa(project, execute_command):
    pa(["env", "--python"])
    execute_command.assert_called_with(["poetry", "env", "--python"], None, exit=True)
