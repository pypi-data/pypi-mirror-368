"""The entry point for SCA2D. This file runs when you run `sca2d` in terminal"""

import os
import sys
import argparse
import json
from sca2d import Analyser
from sca2d.messages import print_messages, count_messages, gitlab_summary, MESSAGES
from sca2d.docs import Documentation


def _parse_ignore_arg(ignore_str):
    to_ignore = set(filter(None, ignore_str.split(",")))
    assert to_ignore.issubset(MESSAGES), (
        f"'--ignore' contains unknown message codes: {to_ignore - set(MESSAGES)}"
    )
    return sorted(to_ignore)


def parse_args(cli_arguments=None):
    """
    This sets up the argument parsing using the argparse module. It will automatically
    create a help message describing all options. Run `sca2d -h` in your terminal to see
    this description.
    """
    parser = argparse.ArgumentParser(
        description="SCA2D - A static code analyser for OpenSCAD."
    )
    parser.add_argument(
        "file_or_dir_name",
        metavar="<file_or_dir_name>",
        type=str,
        help="The .scad file to analyse or the directory to analyse.",
    )
    parser.add_argument(
        "--output-tree",
        help="Output the parse tree to <filename>.sca2d",
        action="store_true",
    )
    parser.add_argument(
        "--colour",
        help=(
            "Use colour when outputting the warning messages."
            "May not work as expected in all terminals."
        ),
        action="store_true",
    )
    parser.add_argument(
        "--docs", help=("Generate documentation after linting."), action="store_true"
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Project title (used only when --docs is specified)",
    )
    parser.add_argument(
        "--verbose", help=("Put SCA2D into verbose mode."), action="store_true"
    )
    parser.add_argument(
        "--debug", help=("Also print SCA2D debug messages"), action="store_true"
    )
    parser.add_argument(
        "--gitlab-report",
        help=("Output a gitlab code quality report"),
        action="store_true",
    )
    parser.add_argument(
        "--ignore",
        type=_parse_ignore_arg,
        help=(
            "Comma-seperated list of message codes to ignore. "
            "Note that some messages cannot be ignored, for instance "
            "fatal syntax errors.  example: --ignore=W2010,W1003"
        ),
        default="",
    )
    return parser.parse_args(cli_arguments)


def _run_on_file(args, analyser):
    [parsed, all_messages] = analyser.analyse_file(
        args.file_or_dir_name, output_tree=args.output_tree, ignore_list=args.ignore
    )
    print_messages(all_messages, args.file_or_dir_name, args.colour, args.debug)
    if args.docs:
        print("Can only generate docs when running on a directory.")
    return [parsed, all_messages]


def _get_all_scad_files(dir_name):
    scad_files = []
    for root, _, files in os.walk(dir_name):
        for name in files:
            if name.endswith(".scad"):
                scad_filename = os.path.join(root, name)
                scad_files.append(scad_filename)
    return scad_files


def _run_on_dir(args, analyser):
    parsed = True
    all_messages = []
    scad_files = _get_all_scad_files(args.file_or_dir_name)
    for scad_filename in scad_files:
        [file_parsed, file_messages] = analyser.analyse_file(
            scad_filename, output_tree=args.output_tree, ignore_list=args.ignore
        )
        print_messages(file_messages, scad_filename, args.colour, args.debug)
        parsed = parsed and file_parsed
        all_messages += file_messages
    if args.docs:
        doc_messages = []
        if any(message.fatal for message in all_messages):
            print("Cannot continue to process documentation due to fatal error.")
        else:
            documentation = Documentation(analyser, scad_files, args)
            documentation.build()
            for im_to_generate in documentation.images:
                ident = im_to_generate[0]
                customisers = im_to_generate[1]
                success, msg = documentation.image_generator.create_image(
                    ident, customisers
                )
                if not success:
                    doc_messages.append(msg)
                    print_messages([msg], "EXAMPLE", args.colour, args.debug)
        all_messages += doc_messages
    return [parsed, all_messages]


def main(cli_arguments=None):
    """
    creates a sca2d analyser and then analyses the input file. Printing
    analysis to the screen
    """
    args = parse_args(cli_arguments)
    analyser = Analyser(verbose=args.verbose)
    if os.path.isfile(args.file_or_dir_name):
        [_, all_messages] = _run_on_file(args, analyser)

    elif os.path.isdir(args.file_or_dir_name):
        [_, all_messages] = _run_on_dir(args, analyser)
    else:
        print("Cannot find file or directory!")
        sys.exit(-1)

    message_summary = count_messages(all_messages)
    print(message_summary)

    if args.gitlab_report:
        with open("gl-code-quality-report.json", "w") as json_file:
            json.dump(gitlab_summary(all_messages), json_file)

    if (message_summary.fatal + message_summary.error) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
