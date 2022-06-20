import os
import sys

import pytest
from onepm import pi, pr, pa, pu, pun
from onepm.pip import Pip

pytestmark = pytest.mark.usefixtures("pip")


@pytest.fixture
def venv(monkeypatch):
    monkeypatch.setenv("VIRTUAL_ENV", "foo")


def test_pip_detect_activated_venv(venv):
    pm = Pip()
    if sys.platform == "win32":
        assert pm.command == ["foo\\Scripts\\python.exe", "-m", "pip"]
    else:
        assert pm.command == ["foo/bin/python", "-m", "pip"]


def test_pip_detect_dot_venv(project):
    project.joinpath(".venv").mkdir()
    project.joinpath(".venv/pyvenv.cfg").touch()
    pm = Pip()
    if sys.platform == "win32":
        assert pm.command == [
            os.path.join(project, ".venv", "Scripts", "python.exe"),
            "-m",
            "pip",
        ]
    else:
        assert pm.command == [
            os.path.join(project, ".venv", "bin", "python"),
            "-m",
            "pip",
        ]


def test_pip_no_venv_error(project):
    with pytest.raises(
        Exception, match="To use pip, you must activate a virtualenv or create one"
    ):
        pi([])


def test_install_without_args_error(project, venv):
    with pytest.raises(
        Exception, match="No requirements.txt or setup.py/pyproject.toml is found"
    ):
        pi([])


@pytest.mark.parametrize("filename", ["requirements.txt", "requirements.in"])
def test_pip_install_without_args_from_requirements_txt(
    project, venv, execute_args, filename
):
    project.joinpath(filename).touch()
    pi([])
    assert execute_args[3:] == ["install", "-r", filename]


@pytest.mark.parametrize("filename", ["setup.py", "pyproject.toml"])
def test_pip_install_without_args_current_project(
    project, venv, execute_args, filename
):
    project.joinpath(filename).touch()
    pi([])
    assert execute_args[3:] == ["install", "."]


def test_pip_install_with_args(project, venv, execute_args):
    pi(["--upgrade", "bar"])
    assert execute_args[3:] == ["install", "--upgrade", "bar"]


def test_pip_run(project, venv, execute_args):
    pr(["bar", "--version"])
    assert execute_args == ["bar", "--version"]


def test_pip_pu_not_supported(project, venv):
    with pytest.raises(Exception, match="pip does not support the `pu` shortcut"):
        pu([])


def test_pip_pun(project, venv, execute_args):
    pun(["bar"])
    assert execute_args[3:] == ["uninstall", "bar"]


def test_pip_pa(project, venv, execute_args):
    pa(["freeze", "--path", "foo"])
    assert execute_args[3:] == ["freeze", "--path", "foo"]
