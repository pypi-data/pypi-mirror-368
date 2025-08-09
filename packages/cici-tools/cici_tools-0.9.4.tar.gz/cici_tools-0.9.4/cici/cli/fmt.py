# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from importlib import import_module
from pathlib import Path

from termcolor import colored

from ..constants import DEFAULT_PROVIDER


def fmt_command(parser, args):
    provider = import_module(f".{DEFAULT_PROVIDER}", "cici.providers")

    if not args.filenames:
        args.filenames = [provider.CI_FILE]

    for filename in args.filenames:
        if not Path(filename).exists():
            parser.error(f"file not found: {filename}")

    for filename in args.filenames:
        file = provider.load(filename)
        with open(filename, "w") as stream:
            provider.dump(file, stream)
        print(colored("formatted", "magenta"), filename)


def fmt_parser(subparsers):
    parser = subparsers.add_parser("fmt", help="format CI files")
    parser.add_argument("filenames", metavar="FILE", nargs="*")
    parser.set_defaults(func=fmt_command)
    return parser
