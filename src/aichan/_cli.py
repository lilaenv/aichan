import argparse
from logging import Logger

from src.aichan.utils.logger import setup_logger


def parse_args_and_setup_logging() -> Logger:
    """Parse command line arguments and set up logging configuration.

    This function initializes argument parsing for command line options
    and sets up the logging configuration for the application.

    Returns
    -------
    logging.Logger
        Configured logger instance with the log level specified
        by the --log command line argument.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log",
        default="INFO",
    )

    args = parser.parse_args()
    # mypy(no-any-return): setup_logger() の戻り値に明示的に型を指定した
    return setup_logger(args.log)  # type: ignore
