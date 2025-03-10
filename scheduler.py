import time
import schedule
import subprocess
from loguru import logger


def job():
    subprocess.run(["python3", "sync_runs.py", "-f", "-t", "1800"])
    logger.info("Sync of runs execute successfully")


if __name__ == "__main__":
    schedule.every(15).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
