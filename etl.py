import csv
import os
import psycopg2
from datetime import datetime
from db import get_connection
import pandas as pd

def extract_data_from_csv(csv_file_path):
    """Extract data from CSV file"""
    data = []
    try:
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                data.append(row)
        print(f"Extracted {len(data)} records from CSV")
        return data
    except Exception as e:
        print(f"Error extracting data: {e}")
        return []

def transform_pet_data(data):
    """Transform pet data to match database schema"""
    transformed_data = []
    for row in data:
        # Convert empty strings to None
        for key, value in row.items():
            if value == '':
                row[key] = None
        
        # Ensure age is an integer
        if row.get('age'):
            try:
                row['age'] = int(row['age'])
            except ValueError:
                row['age'] = None
        
        # Format date if needed
        if row.get('added_date'):
            try:
                # If date format needs conversion
                date_obj = datetime.strptime(row['added_date'], '%Y-%m-%d')
                row['added_date'] = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                row['added_date'] = None
        
        transformed_data.append(row)
    
    print(f"Transformed {len(transformed_data)} records")
    return transformed_data

def load_pets_to_db(data):
    """Load transformed pet data to database"""
    conn = get_connection()
    cur = conn.cursor()
    
    records_inserted = 0
    records_updated = 0
    
    try:
        for pet in data:
            # Check if pet already exists
            cur.execute("SELECT pet_id FROM Pet WHERE pet_id = %s", (pet['pet_id'],))
            existing_pet = cur.fetchone()
            
            if existing_pet:
                # Update existing pet
                cur.execute("""
                    UPDATE Pet 
                    SET name = %s, breed = %s, age = %s, status = %s, added_date = %s
                    WHERE pet_id = %s
                """, (
                    pet['name'], 
                    pet['breed'], 
                    pet['age'], 
                    pet['status'], 
                    pet['added_date'], 
                    pet['pet_id']
                ))
                records_updated += 1
            else:
                # Insert new pet
                cur.execute("""
                    INSERT INTO Pet (pet_id, name, breed, age, status, added_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    pet['pet_id'], 
                    pet['name'], 
                    pet['breed'], 
                    pet['age'], 
                    pet['status'], 
                    pet['added_date']
                ))
                records_inserted += 1
        
        conn.commit()
        print(f"Successfully loaded data: {records_inserted} inserted, {records_updated} updated")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error loading data: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def run_etl_pipeline(csv_file_path):
    """Run the complete ETL pipeline"""
    print(f"Starting ETL pipeline for {csv_file_path}")
    
    # Extract
    raw_data = extract_data_from_csv(csv_file_path)
    if not raw_data:
        print("ETL failed: No data extracted")
        return False
    
    # Transform
    transformed_data = transform_pet_data(raw_data)
    if not transformed_data:
        print("ETL failed: Transformation error")
        return False
    
    # Load
    success = load_pets_to_db(transformed_data)
    if success:
        print("ETL pipeline completed successfully")
        return True
    else:
        print("ETL pipeline failed during load phase")
        return False

if __name__ == "__main__":
    # Run directly if script is executed
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "pets.csv"  # Default file name
    
    run_etl_pipeline(file_path)
