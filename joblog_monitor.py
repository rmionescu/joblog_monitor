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


# ──────────────────────────────── BUSINESS LOGIC ────────────────────────────
def process_log(in_path: Path, out_path: Path, logger: logging.Logger) -> None:

    # Dictionary with the jobs/tasks
    active: dict[str, tuple[str, datetime]] = {}  # pid -> (job, start_dt)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Processing started for file {in_path}")

    # Open the log file for processing and the report file for writing
    with in_path.open() as src, out_path.open(mode="w", newline="") as dest:
        writer = csv.writer(dest)
        writer.writerow(["pid", "job", "duration_sec", "flag"])

        for lineno, raw_line in enumerate(src, 1):
            line = raw_line.strip()
            if not line:
                logger.debug(f"Line {lineno}: empty, skipped")
                continue

            parts = [p.strip() for p in line.split(sep=",", maxsplit=3)]

            # Validate line integrity
            if len(parts) != 4:
                logger.warning(f"Line {lineno} malformed ({len(parts)} fields): {line}")
                continue

            ts_str, job, event, pid = parts

            # Validate timestamp
            try:
                t = datetime.strptime(ts_str, "%H:%M:%S").time()
                ts = datetime.combine(date.today(), t)
            except ValueError:
                logger.warning(f"Line {lineno} bad timestamp '{ts_str}'")
                continue

            event = event.upper()
            if event not in {"START", "END"}:
                logger.warning(f"Line {lineno} unknown event '{event}'")
                continue

            if event == "START":
                if pid in active:
                    logger.warning(f"Line {lineno} duplicate START for pid {pid}; overwriting previous start")
                active[pid] = (job, ts)

            else:   # END
                if pid not in active:
                    logger.warning(f"Line {lineno} END for pid {pid} with no START")
                    continue
                job_desc, start_ts = active.pop(pid)
                duration = (ts - start_ts).total_seconds()

                flag = ""
                if duration >= ERROR_THRESHOLD:
                    flag = "ERROR"
                elif duration >= WARNING_THRESHOLD:
                    flag = "WARNING"

                # Write to the report if the threshold is exceeded
                if flag:
                    writer.writerow([pid, job_desc, f"{duration:.0f}", flag])

    # Anything left open means the job never ended
    for pid, (job_desc, start_ts) in active.items():
        logger.info(f"PID {pid} ({job_desc}) still running, no END found (started {start_ts.time()})")

    logger.info(f"Processing finished. Report saved to {out_path}")


# ──────────────────────────────── MAIN ────────────────────────────
def main(argv: list[str] | None = None) -> None:
    logger = setup_logger(LOG_PATH, LOG_LEVEL)  # Initialize the logger
    logger.info(f"Program started.")

    # Parse the arguments
    parser = usage()
    args = parser.parse_args(argv)
    log_file = args.logfile
    out_file = args.outfile

    logger.debug(f"Provided arguments: {args}")
    logger.debug(f"Log file to analyze: {log_file}")
    logger.debug(f"Report file: {out_file}")

    # Process the log file
    process_log(log_file, out_file, logger)

    logger.info(f"Program ended.")


if __name__ == "__main__":
    main()
