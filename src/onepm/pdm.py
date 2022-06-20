from typing import List, NoReturn

from onepm.base import PackageManager


class PDM(PackageManager):
    name = "pdm"

    def get_command(self) -> List[str]:
        return [self.find_executable(self.name)]

    def install(self, args: List[str]) -> NoReturn:
        self.execute_command(["add"] + list(args))

    def uninstall(self, args: List[str]) -> NoReturn:
        self.execute_command(["remove"] + list(args))

    def update(self, args: List[str]) -> NoReturn:
        self.execute_command(["update"] + list(args))

    def run(self, args: List[str]) -> NoReturn:
        self.execute_command(["run"] + list(args))
