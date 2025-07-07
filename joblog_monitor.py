import csv
import argparse
import logging
from pathlib import Path
from datetime import datetime, date

# ──────────────────────────────── CONFIG ─────────────────────────────────
WARNING_THRESHOLD = 300  # seconds
ERROR_THRESHOLD = 600  # seconds

DATE_STAMP = datetime.now().strftime("%Y-%m-%d")
LOG_DIR = Path("logs")
LOG_PATH = LOG_DIR / f"joblog_monitor_{DATE_STAMP}.log"
LOG_LEVEL = logging.INFO


# ──────────────────────────────── LOG SETUP ─────────────────────────────
def setup_logger(log_path: Path | None = None, level: int = LOG_LEVEL) -> logging.Logger:
    """
    Return a logger that writes to both stderr and an optional file.
    """
    logger = logging.getLogger("joblog_monitor")
    logger.setLevel(level)

    if not logger.handlers:
        fmt = "%(asctime)s [%(levelname)s] %(message)s"
        stream_h = logging.StreamHandler()
        stream_h.setFormatter(logging.Formatter(fmt))
        logger.addHandler(stream_h)

        if log_path:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_h = logging.FileHandler(log_path, mode="a")
            file_h.setFormatter(logging.Formatter(fmt))
            logger.addHandler(file_h)

    return logger


# ──────────────────────────────── USAGE ─────────────────────────────────
def usage() -> argparse.ArgumentParser:
    """
    Construct and return an ArgumentParser for the joblog_monitor .
    """
    parser = argparse.ArgumentParser(
        prog="joblog_monitor",
        description=(
            "Analyse a CSV job log, calculate runtimes, and emit a report "
            "highlighting jobs that exceed certain thresholds."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Mandatory argument: the log file to inspect
    parser.add_argument(
        "logfile",
        type=Path,
        help="Full path to the CSV log file to analyse"
    )

    # Optional argument: output path; if omitted then ./out/report_<timestamp>.csv
    default_stamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    default_out = Path("out") / f"report_{default_stamp}.csv"
    parser.add_argument(
        "-o", "--output",
        dest="outfile",
        type=Path,
        default=default_out,
        help="Full path (including filename) for the generated report CSV"
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    logger = setup_logger(LOG_PATH, LOG_LEVEL)  # Initialize the loger
    logger.info(f"Program started.")

    # Parse the arguments
    parser = usage()
    args = parser.parse_args(argv)
    log_file = args.logfile
    out_file = args.outfile

    logger.debug(f"Provided arguments: {args}")
    logger.debug(f"Log file to analyze: {log_file}")
    logger.debug(f"Report file: {out_file}")

    logger.info(f"Program ended.")


if __name__ == "__main__":
    main()
