from onepm import pi, pa, pu, pun, pr
import pytest

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
def test_pdm_pi_dispatch(project, execute_args, args, expected_command):
    pi(args)
    assert execute_args[1:] == [expected_command] + args


def test_pdm_pr(project, execute_args):
    pr(["test", "--no-report"])
    assert execute_args[1:] == ["run", "test", "--no-report"]


def test_pdm_pu(project, execute_args):
    pu(["-Gtest", "requests"])
    assert execute_args[1:] == ["update", "-Gtest", "requests"]


def test_pdm_pun(project, execute_args):
    pun(["-Gtest", "requests"])
    assert execute_args[1:] == ["remove", "-Gtest", "requests"]


def test_pdm_pa(project, execute_args):
    pa(["config", "--local", "python.use_venv", "on"])
    assert execute_args[1:] == ["config", "--local", "python.use_venv", "on"]
