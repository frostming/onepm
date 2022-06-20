import pytest
from onepm import pi, pa, pu, pun, pr


pytestmark = pytest.mark.usefixtures("pipenv")


@pytest.mark.parametrize("args", [[], ["--dev"], ["--keep-outdated", "requests"]])
def test_pipenv_pi(project, execute_args, args):
    pi(args)
    assert execute_args[1:] == ["install"] + args


def test_pipenv_pr(project, execute_args):
    pr(["test", "--no-report"])
    assert execute_args[1:] == ["run", "test", "--no-report"]


def test_pipenv_pu(project, execute_args):
    pu(["requests"])
    assert execute_args[1:] == ["update", "requests"]


def test_pipenv_pun(project, execute_args):
    pun(["-d", "requests"])
    assert execute_args[1:] == ["uninstall", "-d", "requests"]


def test_pipenv_pa(project, execute_args):
    pa(["--venv", "--system-site-packages", "--python", "3.7"])
    assert execute_args[1:] == [
        "--venv",
        "--system-site-packages",
        "--python",
        "3.7",
    ]
