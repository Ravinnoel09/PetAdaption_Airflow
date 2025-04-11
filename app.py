from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import csv
import json
import datetime
from db import get_connection

# Set up app
app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Home page / Dashboard
@app.route('/')
def index():
    # Add current time and user info for demonstration
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    user = 'dharshan-kumarj'
    return render_template('index.html', current_time=current_time, user=user)

# Serve static files
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/pets', methods=['GET'])
def get_pets():
    status_filter = request.args.get('status')
    
    conn = get_connection()
    cur = conn.cursor()
    
    if status_filter and status_filter != 'all':
        cur.execute("SELECT * FROM Pet WHERE status = %s", (status_filter,))
    else:
        cur.execute("SELECT * FROM Pet")
        
    columns = [desc[0] for desc in cur.description]
    pets = [dict(zip(columns, pet)) for pet in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(pets)

# Dashboard API endpoints
@app.route('/api/dashboard/pet-stats', methods=['GET'])
def pet_stats():
    conn = get_connection()
    cur = conn.cursor()
    
    # Get pet statistics
    cur.execute("""
        SELECT status, COUNT(*) as count FROM Pet GROUP BY status
    """)
    status_counts = [dict(zip(['status', 'count'], row)) for row in cur.fetchall()]
    
    # Get breed statistics
    cur.execute("""
        SELECT breed, COUNT(*) as count FROM Pet GROUP BY breed ORDER BY count DESC LIMIT 5
    """)
    breed_counts = [dict(zip(['breed', 'count'], row)) for row in cur.fetchall()]
    
    # Get age distribution
    cur.execute("""
        SELECT 
            CASE 
                WHEN age < 2 THEN 'Puppy/Kitten (0-1)'
                WHEN age < 5 THEN 'Young (2-4)'
                WHEN age < 9 THEN 'Adult (5-8)'
                ELSE 'Senior (9+)'
            END as age_group,
            COUNT(*) as count
        FROM Pet
        GROUP BY age_group
    """)
    age_distribution = [dict(zip(['age_group', 'count'], row)) for row in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return jsonify({
        'status_counts': status_counts,
        'breed_counts': breed_counts,
        'age_distribution': age_distribution
    })

# ETL CSV processing functions
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
                    SET name = %s, breed = %s, age = %s, status = %s
                    WHERE pet_id = %s
                """, (
                    pet['name'], 
                    pet['breed'], 
                    pet['age'], 
                    pet['status'], 
                    pet['pet_id']
                ))
                records_updated += 1
            else:
                # Insert new pet
                cur.execute("""
                    INSERT INTO Pet (pet_id, name, breed, age, status)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    pet['pet_id'], 
                    pet['name'], 
                    pet['breed'], 
                    pet['age'], 
                    pet['status']
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

# ETL endpoints
@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Run ETL pipeline
        success = run_etl_pipeline(file_path)
        
        if success:
            return jsonify({'message': 'File uploaded and processed successfully on Perfect Cloud'})
        else:
            return jsonify({'error': 'Failed to process the file'}), 500
    
    return jsonify({'error': 'Invalid file format. Please upload a CSV file'}), 400

@app.route('/csv-preview', methods=['POST'])
def csv_preview():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.csv'):
        try:
            # Read the first 10 rows for preview without pandas
            csvfile = file.stream.read().decode('utf-8').splitlines()
            reader = csv.reader(csvfile)
            
            # Get the header row
            header = next(reader)
            
            # Get up to 10 data rows
            data = []
            for i, row in enumerate(reader):
                if i >= 10:  # Only take first 10 rows
                    break
                data.append(dict(zip(header, row)))
            
            return jsonify({
                'columns': header,
                'data': data
            })
        except Exception as e:
            return jsonify({'error': f'Error parsing CSV: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file format. Please upload a CSV file'}), 400

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Check database connection
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'cloud': 'Perfect Cloud',
            'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'user': 'dharshan-kumarj'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Get port from environment variable
    port = int(os.environ.get('PORT', 5000))
    
    # Bind to 0.0.0.0 to make it accessible externally
    app.run(host='0.0.0.0', port=port, debug=False)