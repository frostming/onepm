import pytest

from onepm.core import OneManager


@pytest.fixture
def manager() -> OneManager:
    return OneManager()


@pytest.mark.parametrize("filename", ["Pipfile", "Pipfile.lock"])
def test_detect_pipenv(project, filename, manager):
    project.joinpath(filename).touch()
    assert manager.get_package_manager().name == "pipenv"


def test_detect_pdm_lock(project, manager):
    project.joinpath("pdm.lock").touch()
    assert manager.get_package_manager().name == "pdm"


def test_detect_poetry_lock(project, manager):
    project.joinpath("poetry.lock").touch()
    assert manager.get_package_manager().name == "poetry"


def test_detect_pdm_tool_table(project, manager):
    project.joinpath("pyproject.toml").write_text("[tool.pdm]\n")
    assert manager.get_package_manager().name == "pdm"


def test_detect_poetry_tool_table(project, manager):
    project.joinpath("pyproject.toml").write_text("[tool.poetry]\n")
    assert manager.get_package_manager().name == "poetry"


def test_detect_default_pip(project, manager):
    assert manager.get_package_manager().name == "pip"

    project.joinpath("pyproject.toml").write_text("[tool.black]\n")
    assert manager.get_package_manager().name == "pip"
