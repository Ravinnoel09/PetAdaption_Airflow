import pandas as pd
import psycopg2
from datetime import datetime
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def extract_from_csv(file_path):
    """Extract data from CSV file"""
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Successfully extracted {len(df)} records from {file_path}")
        return df
    except Exception as e:
        logging.error(f"Error extracting data: {e}")
        raise

def transform_data(df):
    """Transform data (basic cleaning and formatting)"""
    try:
        # Convert date strings to datetime objects
        df['added_date'] = pd.to_datetime(df['added_date'])
        
        # Ensure all string columns are properly stripped
        for col in ['name', 'breed', 'status']:
            df[col] = df[col].str.strip()
            
        # Convert age to integer
        df['age'] = df['age'].astype(int)
        
        logging.info("Data transformation completed")
        return df
    except Exception as e:
        logging.error(f"Error transforming data: {e}")
        raise

def load_to_db(df, conn_string):
    """Load data to PostgreSQL database"""
    try:
        # Create connection
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS pets (
            pet_id INTEGER PRIMARY KEY,
            name VARCHAR(100),
            breed VARCHAR(100),
            age INTEGER,
            status VARCHAR(50),
            added_date DATE,
            etl_timestamp TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        
        # Insert data row by row (with error handling)
        inserted = 0
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                INSERT INTO pets (pet_id, name, breed, age, status, added_date, etl_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pet_id) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    breed = EXCLUDED.breed,
                    age = EXCLUDED.age,
                    status = EXCLUDED.status,
                    added_date = EXCLUDED.added_date,
                    etl_timestamp = EXCLUDED.etl_timestamp
                """, (
                    row['pet_id'],
                    row['name'],
                    row['breed'],
                    row['age'],
                    row['status'],
                    row['added_date'],
                    datetime.now()
                ))
                inserted += 1
            except Exception as e:
                logging.error(f"Error inserting record {row['pet_id']}: {e}")
        
        conn.commit()
        logging.info(f"Successfully inserted/updated {inserted} records")
        
    except Exception as e:
        logging.error(f"Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def run_etl():
    """Run the full ETL process"""
    try:
        # File path - get from environment or use default
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file = os.path.join(current_dir, "pets.csv")
        
        # PostgreSQL connection string from environment or use default
        conn_string = os.environ.get(
            "DATABASE_URL", 
            "postgresql://ravin:smKJJp03QRMoJhVanbTZUOtUoQAiCnIM@dpg-cvs9k2mr433s73c1kcb0-a.oregon-postgres.render.com/pet_adoption_tujr"
        )
        
        # ETL process
        logging.info("Starting ETL process")
        df = extract_from_csv(csv_file)
        transformed_df = transform_data(df)
        load_to_db(transformed_df, conn_string)
        logging.info("ETL process completed successfully")
        
    except Exception as e:
        logging.error(f"ETL process failed: {e}")

if __name__ == "__main__":
    run_etl()