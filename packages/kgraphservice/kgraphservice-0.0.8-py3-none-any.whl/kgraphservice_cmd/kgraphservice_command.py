import argparse
import os
import sys


# list endpoints
# get stats of endpoints
# connection test, databases
# connection test, embedding models
# check for collections/graphs for kg
# get stats of collections by type
# get stats of graphs by type
# re-index collection(s), needs embedding model access, via config
# the config specifies embedding model to use with values, types at service level
# can override for collections identified by URI of class


class KGraphServiceCommand:
    def __init__(self, args):
        self.parser = self.create_parser()
        self.args = self.parser.parse_args()
        self.vital_home = os.getenv('VITAL_HOME', '')

    def create_parser(self):

        parser = argparse.ArgumentParser(prog="kgraphservice", description="KGraphService Command", add_help=True)

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        help_parser = subparsers.add_parser('help', help="Display help information")

        info_parser = subparsers.add_parser('info', help="Display information about the system and environment")

        return parser

    def run(self):
        if self.args.command == 'help':
            self.parser.print_help()
        elif self.args.command == 'info':
            self.info()
        else:
            self.parser.print_help()

    def info(self):
        vital_home = self.vital_home
        print("KGraphService Info")
        # list kgraphservices
        # for a given kgraphservice:
        # kgraph, frame, interaction info
        print(f"Current VITAL_HOME: {vital_home}")


def main():
    import sys
    command = KGraphServiceCommand(sys.argv[1:])
    command.run()


if __name__ == "__main__":
    main()
