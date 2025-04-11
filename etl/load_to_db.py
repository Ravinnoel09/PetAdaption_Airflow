"""
Load transformed pet data to database.
"""
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import os

def load_to_postgres(df, table_name, db_connection_string=None):
    """
    Load DataFrame to PostgreSQL database
    
    Args:
        df (pd.DataFrame): Data to load
        table_name (str): Target table name
        db_connection_string (str, optional): Database connection string. 
                                             Defaults to environment variable.
    
    Returns:
        int: Number of rows loaded
    """
    # Get connection string from environment if not provided
    if not db_connection_string:
        db_connection_string = os.environ.get('DATABASE_URL')
        
    if not db_connection_string:
        raise ValueError("Database connection string not provided")
    
    # Create SQLAlchemy engine
    engine = create_engine(db_connection_string)
    
    # Write DataFrame to PostgreSQL
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='replace',  # Use 'append' for incremental loads
        index=False
    )
    
    print(f"Loaded {len(df)} rows to table '{table_name}'")
    return len(df)