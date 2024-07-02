import argparse


def parse_args() -> argparse.Namespace:
    from onepm.core import PACKAGE_MANAGERS

    parser = argparse.ArgumentParser("onepm")
    commands = parser.add_subparsers(dest="command", title="Command")
    commands.add_parser(
        "install", help="Install the package manager configured in project file"
    )
    use_cmd = commands.add_parser(
        "use", help="Use the package manager given by the requirement spec"
    )
    use_cmd.add_argument("spec", help="package manager requirement spec")
    update_cmd = commands.add_parser(
        "update", aliases=["up"], help="Update the package manager used in the project"
    )
    update_cmd.add_argument(
        "name",
        help="The name of package manager",
        choices=PACKAGE_MANAGERS,
        nargs=argparse.OPTIONAL,
    )
    cleanup_cmd = commands.add_parser(
        "cleanup", help="Clean up installations of specified package manager or all"
    )
    cleanup_cmd.add_argument(
        "name",
        nargs=argparse.OPTIONAL,
        choices=list(PACKAGE_MANAGERS),
        help="The name of package manager",
    )
    cleanup_cmd.add_argument(
        "version",
        nargs=argparse.OPTIONAL,
        help="The version of the package to remove",
    )
    list_cmd = commands.add_parser(
        "list",
        aliases=["ls"],
        help="List all installed versions of the given package manager",
    )
    list_cmd.add_argument(
        "name", help="The name of package manager", choices=list(PACKAGE_MANAGERS)
    )
    return parser.parse_args()


def main():
    from onepm.core import OneManager

    args = parse_args()
    core = OneManager()
    match args.command:
        case "install":
            core.get_package_manager()
        case "update" | "up ":
            core.update_package_manager(args.name)
        case "use":
            core.use_package_manager(args.spec)
        case "cleanup":
            core.cleanup(args.name, args.version)
        case "list" | "ls":
            for installation in core.get_installations(args.name):
                print(f"- {installation.version} ({installation.venv})")
