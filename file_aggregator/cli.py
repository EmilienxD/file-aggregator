from __future__ import annotations

import argparse
import sys

from .aggregator import (
    register_target,
    start_watcher,
    remove_target,
    toggle_target,
    list_targets,
)
from .config import set_global_config_path, set_project_config_paths, list_projects_config


def _run(args: argparse.Namespace) -> None:
    project_name = getattr(args, "project", None)
    try:
        if args.command == "register":
            register_target(
                args.target,
                args.sources,
                project_name=project_name,
                into_path=getattr(args, "into", None),
            )
        elif args.command == "watch":
            start_watcher(poll_interval=args.interval, project_name=project_name)
        elif args.command == "remove":
            remove_target(args.target, project_name=project_name)
        elif args.command == "enable":
            toggle_target(args.target, enabled=True, project_name=project_name)
        elif args.command == "disable":
            toggle_target(args.target, enabled=False, project_name=project_name)
        elif args.command == "list":
            list_targets(
                only_enabled=args.enabled,
                project_name=project_name,
                show_config_file=args.show_config,
            )
        elif args.command == "configure":
            if args.configure_cmd == "list":
                default_path, projects = list_projects_config()
                print("Default config (no --project):")
                print(f"  {default_path}")
                print("Projects:")
                if not projects:
                    print("  (none)")
                else:
                    for name, paths in sorted(projects.items()):
                        print(f"  {name}:")
                        for p in paths:
                            print(f"    - {p}")
            elif args.configure_cmd == "path":
                actual_path = set_global_config_path(args.path)
                print(f"Global configuration path set to: {actual_path}")
            elif args.configure_cmd == "project":
                paths = set_project_config_paths(args.name, args.paths)
                print(f"Project {args.name!r} uses {len(paths)} config file(s):")
                for p in paths:
                    print(f"  - {p}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dynamic file aggregator with session persistence.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Projects bundle multiple JSON configs under one name. "
            "Use `fag configure project NAME path1 path2` then `fag -p NAME ...`. "
            "Targets in later files override the same target name in earlier files."
        ),
    )
    parser.add_argument(
        "-p",
        "--project",
        metavar="NAME",
        help="Use the config path list registered for this project name.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_reg = subparsers.add_parser("register", help="Register a target file and its sources.")
    parser_reg.add_argument("target", help="The output dynamic file.")
    parser_reg.add_argument("sources", nargs="+", help="Ordered list of source files.")
    parser_reg.add_argument(
        "--into",
        metavar="PATH",
        help="When using a project with multiple configs, write the new target to this JSON file "
        "(must be one of the project's paths). Defaults to the first file.",
    )

    parser_watch = subparsers.add_parser("watch", help="Start the polling loop for all registered files.")
    parser_watch.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Polling interval in seconds (default: 2.0).",
    )

    parser_rem = subparsers.add_parser("remove", help="Remove a registered target.")
    parser_rem.add_argument("target", help="The target file to remove.")

    parser_en = subparsers.add_parser("enable", help="Enable a registered target.")
    parser_en.add_argument("target", help="The target file to enable.")

    parser_dis = subparsers.add_parser("disable", help="Disable a registered target.")
    parser_dis.add_argument("target", help="The target file to disable.")

    parser_list = subparsers.add_parser("list", help="List all registered targets.")
    parser_list.add_argument("--enabled", action="store_true", help="Only list enabled targets.")
    parser_list.add_argument(
        "-c",
        "--show-config",
        action="store_true",
        help="Show which config file each target comes from.",
    )

    parser_conf = subparsers.add_parser("configure", help="Manage global default path and named projects.")
    conf_sub = parser_conf.add_subparsers(dest="configure_cmd", required=True)

    conf_list = conf_sub.add_parser("list", help="Print default config path and all projects.")
    conf_path = conf_sub.add_parser("path", help="Set the global default aggregator JSON path.")
    conf_path.add_argument("path", help="Path to the aggregator JSON file.")

    conf_proj = conf_sub.add_parser(
        "project",
        help="Set one or more aggregator JSON paths for a named project.",
    )
    conf_proj.add_argument("name", help="Project name.")
    conf_proj.add_argument("paths", nargs="+", help="One or more aggregator JSON paths.")

    args = parser.parse_args()
    _run(args)


if __name__ == "__main__":
    main()
