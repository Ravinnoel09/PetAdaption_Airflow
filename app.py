from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import pandas as pd
from db import get_connection
from etl import run_etl_pipeline
import datetime

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
            return jsonify({'message': 'File uploaded and processed successfully'})
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
            # Read the first 10 rows for preview
            df = pd.read_csv(file, nrows=10)
            return jsonify({
                'columns': list(df.columns),
                'data': df.fillna('').to_dict('records')
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
    app.run(host='0.0.0.0', port=port, debug=True)
