import pytest

from onepm.core import OneManager


@pytest.fixture(autouse=True)
def ensure_excutable(mocker):
    mocker.patch("onepm.pm.pip.Pip.ensure_executable", return_value="python")
    mocker.patch(
        "onepm.pm.base.PackageManager.ensure_executable", return_value="python"
    )


@pytest.mark.parametrize("filename", ["Pipfile", "Pipfile.lock"])
def test_detect_pipenv(project, filename):
    project.joinpath(filename).touch()
    assert OneManager().get_package_manager().name == "pipenv"


def test_detect_pdm_lock(project):
    project.joinpath("pdm.lock").touch()
    assert OneManager().get_package_manager().name == "pdm"


def test_detect_poetry_lock(project):
    project.joinpath("poetry.lock").touch()
    assert OneManager().get_package_manager().name == "poetry"


def test_detect_pdm_tool_table(project):
    project.joinpath("pyproject.toml").write_text("[tool.pdm]\n")
    assert OneManager().get_package_manager().name == "pdm"


def test_detect_poetry_tool_table(project):
    project.joinpath("pyproject.toml").write_text("[tool.poetry]\n")
    assert OneManager().get_package_manager().name == "poetry"


def test_detect_default_pip(project):
    assert OneManager().get_package_manager().name == "pip"

    project.joinpath("pyproject.toml").write_text("[tool.black]\n")
    assert OneManager().get_package_manager().name == "pip"
