import argparse
import os
import sys

from kgraphservice_rest.kgraphservice_rest_app import run_app


class KGraphServiceServer:
    def __init__(self, args):
        self.parser = self.create_parser()
        self.args = self.parser.parse_args()

        vital_home = os.getenv('VITAL_HOME', '')

        print(f"VITAL_HOME: {vital_home}")

        self.vital_home = vital_home

    def create_parser(self):

        parser = argparse.ArgumentParser(prog="kgraphservice", description="KGraphServiceServer", add_help=True)

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        help_parser = subparsers.add_parser('help', help="Display help information")

        info_parser = subparsers.add_parser('info', help="Display information about the system and environment")

        start_parser = subparsers.add_parser('start', help="Start Server")

        return parser

    def run(self):
        if self.args.command == 'help':
            self.parser.print_help()
        elif self.args.command == 'info':
            self.info()
        elif self.args.command == 'start':
            self.start()
        else:
            self.parser.print_help()

    def info(self):
        vital_home = self.vital_home
        print("KGraphServiceServer Info")
        print(f"Current VITAL_HOME: {vital_home}")

    def start(self):
        vital_home = self.vital_home
        print("KGraphServiceServer Start")
        print(f"Current VITAL_HOME: {vital_home}")

        host = "0.0.0"
        port = 6008

        run_app(host=host, port=port)


def main():
    import sys
    command = KGraphServiceServer(sys.argv[1:])
    command.run()


if __name__ == "__main__":
    main()
