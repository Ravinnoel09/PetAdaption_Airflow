#!/usr/bin/env python3
import json
import os
import psycopg2
import logging
from datetime import datetime, date

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Custom JSON encoder to handle date objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

def get_pet_data(conn_string):
    """Get pet data from database"""
    try:
        # Create connection
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        
        # Get pet data
        cursor.execute("""
        SELECT pet_id, name, breed, age, status, added_date, etl_timestamp
        FROM pets
        ORDER BY pet_id
        """)
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            result = dict(zip(columns, row))
            results.append(result)
            
        return results
        
    except Exception as e:
        logging.error(f"Error getting pet data: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def get_log_entries(log_file_path):
    """Get log entries from log file"""
    try:
        if not os.path.exists(log_file_path):
            return []
            
        with open(log_file_path, 'r') as f:
            log_lines = f.readlines()
            
        # Get the last 100 log entries (or fewer if there are less)
        return [line.strip() for line in log_lines[-100:]]
        
    except Exception as e:
        logging.error(f"Error reading log file: {e}")
        return []

def get_etl_metrics(log_entries):
    """Extract ETL metrics from log entries"""
    metrics = {
        'last_successful_run': None,
        'status': 'Unknown',
        'total_records': 0
    }
    
    for line in reversed(log_entries):
        if 'ETL process completed successfully' in line:
            # Found the last successful run
            timestamp = line.split(' - ')[0]
            metrics['last_successful_run'] = timestamp
            metrics['status'] = 'Success'
            break
        elif 'ETL process failed' in line:
            # Found a failure
            timestamp = line.split(' - ')[0]
            metrics['last_successful_run'] = timestamp
            metrics['status'] = 'Failed'
            break
    
    # Find the number of records processed
    for line in reversed(log_entries):
        if 'Successfully inserted/updated' in line:
            parts = line.split('Successfully inserted/updated')
            if len(parts) > 1:
                count_part = parts[1].strip()
                try:
                    metrics['total_records'] = int(count_part.split(' ')[0])
                except:
                    pass
            break
    
    return metrics

def update_dashboard_data():
    """Update the dashboard data JSON file"""
    try:
        # Get database connection string from environment or use default
        conn_string = os.environ.get(
            "DATABASE_URL", 
            "postgresql://ravin:smKJJp03QRMoJhVanbTZUOtUoQAiCnIM@dpg-cvs9k2mr433s73c1kcb0-a.oregon-postgres.render.com/pet_adoption_tujr"
        )
        
        # Get pet data
        pet_data = get_pet_data(conn_string)
        
        # Get log entries
        log_file_path = os.environ.get("LOG_FILE_PATH", "pet_etl.log")
        log_entries = get_log_entries(log_file_path)
        
        # Get ETL metrics
        metrics = get_etl_metrics(log_entries)
        
        # Create dashboard data
        dashboard_data = {
            'pet_data': pet_data,
            'log_entries': log_entries,
            'metrics': metrics,
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save to JSON file using the custom encoder
        with open('dashboard_data.json', 'w') as f:
            json.dump(dashboard_data, f, indent=2, cls=DateTimeEncoder)
            
        logging.info(f"Dashboard data updated successfully. Found {len(pet_data)} pets and {len(log_entries)} log entries.")
        
    except Exception as e:
        logging.error(f"Error updating dashboard data: {e}")

if __name__ == "__main__":
    update_dashboard_data()