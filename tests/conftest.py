import os

import pytest

from onepm.core import OneManager


@pytest.fixture()
def execute_command(mocker):
    return mocker.patch("onepm.pm.base.PackageManager._execute_command")


@pytest.fixture()
def project(tmp_path):
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(cwd)


@pytest.fixture()
def pip(mocker, project):
    with open("pyproject.toml", "a") as f:
        f.write('[tool.onepm]\npackage-manager = "pip"\n')
    mocker.patch("onepm.pm.pip.Pip.ensure_executable", return_value="python")
    assert OneManager().get_package_manager().name == "pip"


@pytest.fixture()
def poetry(mocker, project):
    with open("pyproject.toml", "a") as f:
        f.write('[tool.onepm]\npackage-manager = "poetry"\n')
    mocker.patch("onepm.pm.poetry.Poetry.ensure_executable", return_value="poetry")
    assert OneManager().get_package_manager().name == "poetry"


@pytest.fixture()
def pipenv(mocker, project):
    with open("pyproject.toml", "a") as f:
        f.write('[tool.onepm]\npackage-manager = "pipenv"\n')
    mocker.patch("onepm.pm.pipenv.Pipenv.ensure_executable", return_value="pipenv")
    assert OneManager().get_package_manager().name == "pipenv"


@pytest.fixture()
def pdm(mocker, project):
    with open("pyproject.toml", "a") as f:
        f.write('[tool.onepm]\npackage-manager = "pdm"')
    mocker.patch("onepm.pm.pdm.PDM.ensure_executable", return_value="pdm")
    assert OneManager().get_package_manager().name == "pdm"


@pytest.fixture()
def uv(mocker, project):
    with open("pyproject.toml", "a") as f:
        f.write('[tool.onepm]\npackage-manager = "uv"')
    mocker.patch("onepm.pm.uv.Uv.ensure_executable", return_value="uv")
    assert OneManager().get_package_manager().name == "uv"
