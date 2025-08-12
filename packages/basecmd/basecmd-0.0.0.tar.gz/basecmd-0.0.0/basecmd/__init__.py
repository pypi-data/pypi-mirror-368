#!/usr/bin/env python3

"""
Logging boilerplate for the command line.
"""

import logging
import sys
from argparse import ArgumentParser, Namespace
from functools import cached_property

from colors import color, red, white, yellow
from decouple import Choices, config

__all__ = ("BaseCmd",)
__version__ = "0.1.6"


class BaseCmd:
    "Provide logging and related command-line arguments"

    LOG_FORMAT: str | None = config("LOG_FORMAT", default=None)  # type: ignore

    # Map verbosity argument to log level
    LOG_LEVELS = {
        "error": logging.ERROR,
        "warn": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG,
    }

    options: Namespace
    log: logging.Logger

    class ColorFormatter(logging.Formatter):
        "Color log output by log level"

        # See: https://stackoverflow.com/a/56944256

        def __init__(self, format):
            self.default_formatter = logging.Formatter(format)
            self.formats = {
                logging.DEBUG: logging.Formatter(color(format, style="faint")),
                logging.INFO: logging.Formatter(white(format)),
                logging.WARNING: logging.Formatter(yellow(format)),
                logging.ERROR: logging.Formatter(red(format)),
                logging.CRITICAL: logging.Formatter(
                    color(format, fg="red", style="bold")
                ),
            }

        def format(self, record) -> str:
            return self.formats.get(record.levelno, self.default_formatter).format(
                record
            )

    def __init__(self, **kw):
        self.parse_args()
        self.init_logging()
        super(BaseCmd, self).__init__(**kw)

    def add_arguments(self) -> None:
        "Hook for subclasses to add additional command line options"
        pass

    def parse_args(self, args=None) -> None:
        self.parser = ArgumentParser(description=self.__doc__)

        self.parser.add_argument(
            "-v",
            "--verbosity",
            choices=self.LOG_LEVELS.keys(),
            default=config(
                "LOG_LEVEL", default="info", cast=Choices(self.LOG_LEVELS.keys())
            ),
            help="Logging verbosity",
        )

        self.parser.add_argument(
            "--log-file",
            help="File path for logging",
            default=config("LOG_FILE", default=None),
        )

        self.add_arguments()
        self.options = self.parser.parse_args(args)

    def init_logging(self) -> None:
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(self.LOG_LEVELS[self.options.verbosity])

        if self.options.log_file:
            logging.basicConfig(filename=self.options.log_file)
        else:
            logging.basicConfig(stream=sys.stdout)

        if self.LOG_FORMAT is None:
            self.LOG_FORMAT = "%(asctime).19s  %(message)s"

        if self.tty_log:
            self.rootHandler.setFormatter(self.ColorFormatter(self.LOG_FORMAT))
        else:
            self.rootHandler.setFormatter(logging.Formatter(self.LOG_FORMAT))

    @cached_property
    def rootHandler(self) -> logging.Handler:
        return logging.getLogger().handlers[0]

    @cached_property
    def tty_log(self) -> bool:
        return (
            type(self.rootHandler) is logging.StreamHandler
            and self.rootHandler.stream.isatty()
        )
