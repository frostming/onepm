import os
from unittest import mock
import pytest


@pytest.fixture()
def execute_args(monkeypatch):
    call_args = []

    @staticmethod
    def fake_execute(args):
        call_args[:] = args

    monkeypatch.setattr("onepm.base.PackageManager._execute_command", fake_execute)
    return call_args


@pytest.fixture()
def project(tmp_path):
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(cwd)


@pytest.fixture()
def pip(monkeypatch):
    monkeypatch.setattr(
        "onepm.determine_package_manager", mock.Mock(return_value="pip")
    )


@pytest.fixture()
def poetry(monkeypatch):
    monkeypatch.setattr(
        "onepm.determine_package_manager", mock.Mock(return_value="poetry")
    )
    monkeypatch.setattr(
        "onepm.base.PackageManager.find_executable", mock.Mock(return_value="poetry")
    )


@pytest.fixture()
def pipenv(monkeypatch):
    monkeypatch.setattr(
        "onepm.determine_package_manager", mock.Mock(return_value="pipenv")
    )
    monkeypatch.setattr(
        "onepm.base.PackageManager.find_executable", mock.Mock(return_value="pipenv")
    )


@pytest.fixture()
def pdm(monkeypatch):
    monkeypatch.setattr(
        "onepm.determine_package_manager", mock.Mock(return_value="pdm")
    )
    monkeypatch.setattr(
        "onepm.base.PackageManager.find_executable", mock.Mock(return_value="pdm")
    )
