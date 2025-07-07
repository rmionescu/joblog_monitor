# JobLog Monitor

`joblog_monitor.py` is a script that analyzes a CSV log file containing job start and end events, calculates runtimes, and generates a report highlighting jobs that exceed defined thresholds.

## Usage

```bash
python joblog_monitor.py [-h] [-o OUTFILE] logfile
```
- logfile (required): Full path to the CSV log file to analyze.
- -o, --output (optional): Full path to the output report file. (If not provided, a report will be saved to ./out/report_\<timestamp>.csv.)

## Configuration
Edit the joblog_monitor.py script directly to configure behavior.
Thresholds:
- WARNING_THRESHOLD = 300  # seconds (5 minutes)
- ERROR_THRESHOLD   = 600  # seconds (10 minutes)

Logging level. Set the desired log verbosity:
- LOG_LEVEL = logging.INFO *(Other options: logging.DEBUG, logging.WARNING, logging.ERROR)*