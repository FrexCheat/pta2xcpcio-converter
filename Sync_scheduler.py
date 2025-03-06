import time
import schedule
import subprocess
from loguru import logger


def job():
    subprocess.run(["python3", "Sync_runs.py"])
    logger.info("Sync of runs execute successfully")


if __name__ == "__main__":
    schedule.every(30).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
