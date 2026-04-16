import argparse
from .aggregator import register_target, start_watcher, remove_target, toggle_target, list_targets

def main():
    parser = argparse.ArgumentParser(description="Dynamic file file aggregator with session persistence.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Register Command
    parser_reg = subparsers.add_parser("register", help="Register a target file and its sources.")
    parser_reg.add_argument("target", help="The output dynamic file.")
    parser_reg.add_argument("sources", nargs="+", help="Ordered list of source files.")
    
    # Watch Command
    parser_watch = subparsers.add_parser("watch", help="Start the polling loop for all registered files.")
    parser_watch.add_argument("--interval", type=float, default=2.0, help="Polling interval in seconds (default: 2.0).")

    # Remove Command
    parser_rem = subparsers.add_parser("remove", help="Remove a registered target.")
    parser_rem.add_argument("target", help="The target file to remove.")

    # Enable/Disable Commands
    parser_en = subparsers.add_parser("enable", help="Enable a registered target.")
    parser_en.add_argument("target", help="The target file to enable.")

    parser_dis = subparsers.add_parser("disable", help="Disable a registered target.")
    parser_dis.add_argument("target", help="The target file to disable.")

    # List Command
    parser_list = subparsers.add_parser("list", help="List all registered targets.")
    parser_list.add_argument("--enabled", action="store_true", help="Only list enabled targets.")

    args = parser.parse_args()

    if args.command == "register":
        register_target(args.target, args.sources)
    elif args.command == "watch":
        start_watcher(poll_interval=args.interval)
    elif args.command == "remove":
        remove_target(args.target)
    elif args.command == "enable":
        toggle_target(args.target, enabled=True)
    elif args.command == "disable":
        toggle_target(args.target, enabled=False)
    elif args.command == "list":
        list_targets(only_enabled=args.enabled)

if __name__ == "__main__":
    main()
