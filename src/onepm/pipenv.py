from typing import List, NoReturn

from onepm.base import PackageManager


class Pipenv(PackageManager):
    name = "pipenv"

    def get_command(self) -> List[str]:
        return [self.find_executable(self.name)]

    def install(self, *args: str) -> NoReturn:
        self.execute("install", *args)

    def uninstall(self, *args: str) -> NoReturn:
        self.execute("uninstall", *args)

    def update(self, *args: str) -> NoReturn:
        self.execute("update", *args)

    def run(self, *args: str) -> NoReturn:
        self.execute("run", *args)
