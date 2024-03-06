import os
import sys
import venv

import pytest

from onepm import pa, pi, pr, pu, pun
from onepm.core import OneManager


@pytest.fixture
def find_executable(mocker):
    @staticmethod
    def mock_find_executable(name: str, path: str | None = None) -> str:
        return name

    mocker.patch(
        "onepm.pm.base.PackageManager.find_executable", side_effect=mock_find_executable
    )


def test_pip_detect_activated_venv(project, monkeypatch):
    venv.create("foo", clear=True, with_pip=True)
    monkeypatch.setenv("VIRTUAL_ENV", "foo")
    pm = OneManager().get_package_manager()
    assert pm.name == "pip"
    if sys.platform == "win32":
        assert pm.get_command() == ["foo\\Scripts\\python.EXE", "-m", "pip"]
    else:
        assert pm.get_command() == ["foo/bin/python", "-m", "pip"]


@pytest.mark.parametrize("pre_create", [True, False])
def test_pip_detect_dot_venv(project, pre_create, monkeypatch):
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    if pre_create:
        venv.create(".venv", clear=True, with_pip=True)
    pm = OneManager().get_package_manager()
    assert os.path.exists(".venv/pyvenv.cfg")
    assert pm.name == "pip"
    if sys.platform == "win32":
        assert pm.get_command() == [".venv\\Scripts\\python.EXE", "-m", "pip"]
    else:
        assert pm.get_command() == [".venv/bin/python", "-m", "pip"]


@pytest.mark.usefixtures("pip")
def test_install_without_args_error(project, execute_command):
    with pytest.raises(
        Exception, match="No requirements.txt or setup.py/pyproject.toml is found"
    ):
        pi([])


@pytest.mark.usefixtures("pip")
@pytest.mark.parametrize("filename", ["requirements.txt", "requirements.in"])
def test_pip_install_without_args_from_requirements_txt(
    project, execute_command, filename
):
    project.joinpath(filename).touch()
    pi([])
    execute_command.assert_called_with(
        ["python", "-m", "pip", "install", "-r", filename], None, exit=True
    )


@pytest.mark.usefixtures("pip")
def test_pip_install_with_args(project, execute_command):
    pi(["--upgrade", "bar"])
    execute_command.assert_called_with(
        ["python", "-m", "pip", "install", "--upgrade", "bar"], None, exit=True
    )


@pytest.mark.usefixtures("pip")
def test_pip_run(project, find_executable, execute_command):
    pr(["bar", "--version"])
    execute_command.assert_called_with(["bar", "--version"])


@pytest.mark.usefixtures("pip")
def test_pip_pu_not_supported(project):
    with pytest.raises(Exception, match="pip does not support the `pu` shortcut"):
        pu([])


@pytest.mark.usefixtures("pip")
def test_pip_pun(project, execute_command):
    pun(["bar"])
    execute_command.assert_called_with(
        ["python", "-m", "pip", "uninstall", "bar"], None, exit=True
    )


@pytest.mark.usefixtures("pip")
def test_pip_pa(project, execute_command):
    pa(["freeze", "--path", "foo"])
    execute_command.assert_called_with(
        ["python", "-m", "pip", "freeze", "--path", "foo"], None, exit=True
    )
