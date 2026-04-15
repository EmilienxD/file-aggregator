import argparse
from .aggregator import register_target, start_watcher

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

    args = parser.parse_args()

    if args.command == "register":
        register_target(args.target, args.sources)
    elif args.command == "watch":
        start_watcher(poll_interval=args.interval)

if __name__ == "__main__":
    main()
