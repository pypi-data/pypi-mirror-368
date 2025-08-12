# leafsdk/cli/leafcli.py

import argparse
from  cli import upload, validate, start, abort, monitor, wizard

def main():
    parser = argparse.ArgumentParser(description="LeafSDK CLI")
    subparsers = parser.add_subparsers(dest="command")

    upload_parser = subparsers.add_parser('upload', help='Upload a mission')
    upload.add_arguments(upload_parser)

    validate_parser = subparsers.add_parser('validate', help='Validate a mission')
    validate.add_arguments(validate_parser)

    start_parser = subparsers.add_parser('start', help='Start mission execution')
    start.add_arguments(start_parser)

    abort_parser = subparsers.add_parser('abort', help='Abort mission and return home')
    abort.add_arguments(abort_parser)

    monitor_parser = subparsers.add_parser('monitor', help='Monitor mission status')
    monitor.add_arguments(monitor_parser)

    wizard_parser = subparsers.add_parser('wizard', help='Create a mission via wizard')
    wizard.add_arguments(wizard_parser)

    args = parser.parse_args()

    if args.command == "upload":
        upload.run(args)
    elif args.command == "validate":
        validate.run(args)
    elif args.command == "start":
        start.run(args)
    elif args.command == "abort":
        abort.run(args)
    elif args.command == "monitor":
        monitor.run(args)
    elif args.command == "wizard":
        wizard.run(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
