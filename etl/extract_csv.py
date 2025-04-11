"""
Extract data from CSV sources.
"""
import pandas as pd
import os
from datetime import datetime

def extract_pet_data(csv_path):
    """
    Extract pet data from CSV file
    
    Args:
        csv_path (str): Path to CSV file
    
    Returns:
        pd.DataFrame: DataFrame containing pet data
    """
    print(f"Extracting data from {csv_path}")
    
    # Handle remote URLs or local files
    if csv_path.startswith('http'):
        df = pd.read_csv(csv_path)
    else:
        # Check if file exists
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
    
    # Add extraction timestamp
    df['extraction_timestamp'] = datetime.now().isoformat()
    
    print(f"Extracted {len(df)} rows")
    return df