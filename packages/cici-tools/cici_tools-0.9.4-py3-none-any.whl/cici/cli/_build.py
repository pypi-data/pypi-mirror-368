# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import logging
import sys
from importlib import import_module
from pathlib import Path

from ..constants import DEFAULT_PROVIDER, PROVIDERS


def build_command(parser, args):
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    input_provider = import_module(f".{args.input_format}", "cici.providers")
    output_provider = import_module(f".{args.output_format}", "cici.providers")

    if not args.filename:
        args.filename = input_provider.CI_FILE

    if not Path(args.filename).exists():
        parser.error(f"file not found: {args.filename}")

    file = input_provider.load(args.filename)
    output_provider.dump(file, sys.stdout)


def build_parser(subparsers):
    parser = subparsers.add_parser(
        "build", help="build saferatday0 CI file into target format"
    )
    parser.add_argument("filename", nargs="?")
    parser.add_argument(
        "-f",
        "--from",
        dest="input_format",
        choices=PROVIDERS,
        default=DEFAULT_PROVIDER,
        help=f"input format [{DEFAULT_PROVIDER}]",
    )
    parser.add_argument(
        "-t",
        "--to",
        dest="output_format",
        choices=PROVIDERS,
        default=DEFAULT_PROVIDER,
        help=f"output format [{DEFAULT_PROVIDER}]",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        dest="output_path",
        type=Path,
        default=Path.cwd().absolute(),
    )
    parser.set_defaults(func=build_command)
    return parser
