"""
Transform pet data for analysis.
"""
import pandas as pd

def clean_pet_data(df):
    """
    Clean pet data by handling missing values and standardizing formats
    
    Args:
        df (pd.DataFrame): Raw pet data
    
    Returns:
        pd.DataFrame: Cleaned pet data
    """
    # Create a copy to avoid modifying the original
    df_clean = df.copy()
    
    # Standardize column names
    df_clean.columns = [col.lower().replace(' ', '_') for col in df_clean.columns]
    
    # Handle missing values
    if 'age' in df_clean.columns:
        df_clean['age'] = df_clean['age'].fillna('Unknown')
    
    if 'breed' in df_clean.columns:
        df_clean['breed'] = df_clean['breed'].fillna('Mixed')
    
    # Add processing timestamp
    df_clean['processed_timestamp'] = pd.Timestamp.now().isoformat()
    
    print(f"Transformed data: {len(df_clean)} rows processed")
    return df_clean