#!/usr/bin/env python3
import time
import subprocess
import logging
import os
from datetime import datetime
import importlib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Interval in seconds (2 minutes = 120 seconds)
INTERVAL = 120

def run_etl():
    """Run the ETL script by importing and executing it"""
    try:
        logging.info(f"Starting ETL process at {datetime.now()}")
        
        # Import and run the ETL module directly
        # This is better than using subprocess on Render
        etl_module = importlib.import_module('etl')
        if hasattr(etl_module, 'run_etl'):
            etl_module.run_etl()
            logging.info(f"ETL process completed successfully")
        else:
            logging.error("ETL module doesn't have run_etl function")
            
    except Exception as e:
        logging.error(f"Error running ETL process: {e}")

def main():
    """Main function that runs in a loop"""
    logging.info(f"Background ETL worker started at {datetime.now()}")
    logging.info(f"Will run ETL every {INTERVAL} seconds")
    
    # Run immediately on startup
    run_etl()
    
    # Then run on schedule
    try:
        while True:
            logging.info(f"Waiting {INTERVAL} seconds before next run...")
            time.sleep(INTERVAL)
            run_etl()
            
    except KeyboardInterrupt:
        logging.info("Process terminated by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()