import pytest

from onepm import determine_package_manager


@pytest.mark.parametrize("filename", ["Pipfile", "Pipfile.lock"])
def test_detect_pipenv(project, filename):
    project.joinpath(filename).touch()
    assert determine_package_manager().name == "pipenv"


def test_detect_pdm_lock(project):
    project.joinpath("pdm.lock").touch()
    assert determine_package_manager().name == "pdm"


def test_detect_poetry_lock(project):
    project.joinpath("poetry.lock").touch()
    assert determine_package_manager().name == "poetry"


def test_detect_pdm_tool_table(project):
    project.joinpath("pyproject.toml").write_text("[tool.pdm]\n")
    assert determine_package_manager().name == "pdm"


def test_detect_poetry_tool_table(project):
    project.joinpath("pyproject.toml").write_text("[tool.poetry]\n")
    assert determine_package_manager().name == "poetry"


def test_detect_default_pip(project):
    assert determine_package_manager().name == "pip"

    project.joinpath("pyproject.toml").write_text("[tool.black]\n")
    assert determine_package_manager().name == "pip"
