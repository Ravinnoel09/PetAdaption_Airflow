#!/usr/bin/env python3
import time
import subprocess
import logging
import os
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='background_etl.log'
)

# Path to your ETL script
ETL_SCRIPT = '/home/dharshan/web-projects/apacheairflow-ravin/etl.py'
# Path to your Python interpreter
PYTHON_INTERPRETER = '/home/dharshan/web-projects/apacheairflow-ravin/etl/bin/python3'
# Interval in seconds (2 minutes = 120 seconds)
INTERVAL = 120

def run_etl():
    """Run the ETL script as a subprocess"""
    try:
        logging.info(f"Starting ETL process at {datetime.now()}")
        
        # Run the ETL script as a subprocess
        process = subprocess.run(
            [PYTHON_INTERPRETER, ETL_SCRIPT],
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )
        
        # Log output
        if process.stdout:
            logging.info(f"ETL output: {process.stdout}")
        if process.stderr:
            logging.error(f"ETL error: {process.stderr}")
            
        if process.returncode == 0:
            logging.info(f"ETL process completed successfully")
        else:
            logging.error(f"ETL process failed with return code: {process.returncode}")
            
    except Exception as e:
        logging.error(f"Error running ETL process: {e}")

def main():
    """Main function that runs in a loop"""
    logging.info(f"Background ETL runner started at {datetime.now()}")
    logging.info(f"Will run ETL every {INTERVAL} seconds")
    
    try:
        while True:
            # Run the ETL process
            run_etl()
            
            # Wait for the next interval
            logging.info(f"Waiting {INTERVAL} seconds before next run...")
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        logging.info("Process terminated by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()