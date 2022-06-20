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
def test_poetry_pi_dispatch(project, execute_args, args, expected_command):
    pi(args)
    assert execute_args[1:] == [expected_command] + args


def test_poetry_pu(project, execute_args):
    pu(["requests"])
    assert execute_args[1:] == ["update", "requests"]


def test_poetry_pun(project, execute_args):
    pun(["requests"])
    assert execute_args[1:] == ["remove", "requests"]


def test_poetry_pr(project, execute_args):
    pr(["test", "--no-report"])
    assert execute_args[1:] == ["run", "test", "--no-report"]


def test_poetry_pa(project, execute_args):
    pa(["env", "--python"])
    assert execute_args[1:] == ["env", "--python"]
