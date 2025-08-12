from argparse import ArgumentParser as ArgumentParserBase, RawDescriptionHelpFormatter
from gettext import gettext as _
from sys import stderr
from wowool.io.console import console


class ArgumentParser(ArgumentParserBase):
    def __init__(self, *args, **kwargs):
        self.parser = ArgumentParserBase(
            *args, formatter_class=RawDescriptionHelpFormatter, **kwargs
        )

    def __call__(self, *argv):
        args = self.parse_args(*argv)
        kwargs = dict(args._get_kwargs())
        return kwargs

    def error(self, message: str):
        self.print_usage(stderr)
        args = {"prog": self.prog, "message": message}
        self.exit(
            2, _("<prog>%(prog)s</prog>: <error>error</error>: %(message)s\n") % args
        )

    def _print_message(self, message, file=None):
        if message:
            if file is None:
                file = stderr
            console.print(message, file=file)
