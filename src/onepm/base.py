import abc
import os
import shutil
import subprocess
import sys
from typing import List, NoReturn


class PackageManager(metaclass=abc.ABCMeta):
    name: str

    def __init__(self) -> None:
        self.command = self.get_command()

    @staticmethod
    def find_executable(name: str) -> str:
        # TODO: to keep it simple, only search in PATH(no alias/shell function)
        executable = shutil.which(name)
        if not executable:
            raise Exception(f"{name} is not found in PATH, did you install it?")
        return executable

    def execute_command(self, args: List[str]) -> NoReturn:
        command_args = self.command + args
        if sys.platform == "win32":
            sys.exit(subprocess.run(command_args).returncode)
        else:
            os.execvp(command_args[0], command_args)

    @abc.abstractmethod
    def get_command(self) -> List[str]:
        pass

    @abc.abstractmethod
    def install(self, args: List[str]) -> NoReturn:
        pass

    @abc.abstractmethod
    def uninstall(self, args: List[str]) -> NoReturn:
        pass

    @abc.abstractmethod
    def update(self, args: List[str]) -> NoReturn:
        pass

    @abc.abstractmethod
    def run(self, args: List[str]) -> NoReturn:
        pass
