#!/usr/bin/env python
"""\
Update project metadata.\
"""

import argparse
import logging
import pathlib
import subprocess
import sys

import yaml

from .common import ENCODING, NAME
from .config import CONFIG_EXAMPLE, CONFIG_FILE
from .exception import PrometaException
from .project import Project

LOGGER = logging.getLogger(__name__)


def main(args=None):
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description=__doc__, prog=NAME)
    parser.add_argument("path", nargs="*", help="Path to project directory.")
    parser.add_argument(
        "--config",
        metavar="PATH",
        nargs="+",
        type=pathlib.Path,
        help=f"""
            By default, %(prog)s will search for configuration files named
            "{CONFIG_FILE}" or ".{CONFIG_FILE}" in the target directory and all
            of its parent directories, with precedence given to configuration
            files closest to the target directory. Additional configuration file
            paths can be passed with this option and they will take precedence
            over the detected configuration files. If multiple configuration
            paths are given with this command, their order determines their
            precedence.
            """,
    )
    parser.add_argument(
        "--gen-config",
        metavar="PATH",
        help=f"""
            Generate a configuration file template at the given path. If the
            path is "-", the file will be printed to STDOUT. Note that %(prog)s
            will only look for files named "{CONFIG_FILE}" or ".{CONFIG_FILE}".
            """,
    )
    parser.add_argument(
        "--list-config",
        choices=("all", "existing"),
        help="""
            List either all paths that will be scanned for configuration files
            for each given project, or only existing ones. The output is printed
            as a YAML file mapping project directory paths to lists of possible
            configuration files.
            """,
    )
    parser.add_argument(
        "--no-xdg",
        action="store_true",
        help="""
            Disable loading of configuration files in standard XDG locations.
            """,
    )
    parser.add_argument(
        "--trust",
        action="store_true",
        help="""
            It is possible to insert arbitrary command output into the README
            file. By default, %(prog)s will prompt the user for confirmation
            before running the command to prevent arbitrary code execution in
            the context of a collaborative environment. This option can be used
            to disable the prompt if the user trusts all of the commands in the
            README.
            """,
    )
    pargs = parser.parse_args(args=args)

    if pargs.gen_config:
        if pargs.gen_config == "-":
            print(CONFIG_EXAMPLE)
        else:
            path = pathlib.Path(pargs.gen_config).resolve()
            LOGGER.info("Creating %s", path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(CONFIG_EXAMPLE, encoding=ENCODING)
        return

    config_args = {
        "custom_config_paths": pargs.config,
        "trust_commands": pargs.trust,
        "use_xdg": not pargs.no_xdg,
    }

    if pargs.list_config:
        paths = {}
        for path in pargs.path:
            proj = Project(path, **config_args)
            config_paths = (
                proj.config.possible_config_paths
                if pargs.list_config == "all"
                else proj.config.config_paths
            )
            paths[str(path)] = list(str(p) for p in config_paths)
        print(yaml.dump(paths))
        return

    for path in pargs.path:
        LOGGER.info("Updating %s", path)
        proj = Project(path, **config_args)
        proj.update()


def configure_logging(level=logging.INFO):
    """
    Configure logging.

    Args:
        level:
            The logging level.
    """
    logging.basicConfig(
        style="{", format="[{asctime}] {levelname} {message}", level=level
    )


def run_main(args=None):
    """
    Wrapper around main for exception handling.
    """
    configure_logging()
    try:
        main(args=args)
    except KeyboardInterrupt:
        pass
    except (PrometaException, subprocess.CalledProcessError) as err:
        sys.exit(err)


if __name__ == "__main__":
    run_main()
