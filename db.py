import os
import psycopg2

def get_connection():
    """Get database connection using environment variables or defaults"""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "pet_adoption_tujr"),
        user=os.getenv("DB_USER", "ravin"),
        password=os.getenv("DB_PASSWORD", "smKJJp03QRMoJhVanbTZUOtUoQAiCnIM"),
        host=os.getenv("DB_HOST", "dpg-cvs9k2mr433s73c1kcb0-a.oregon-postgres.render.com"),
        port=os.getenv("DB_PORT", "5432")
    )

# Test connection
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("Database connection successful!")
        conn.close()
    except Exception as e:
        print(f"Database connection failed: {e}")
