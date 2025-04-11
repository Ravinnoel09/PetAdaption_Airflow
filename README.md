# Pet Adoption ETL Project

A simple ETL (Extract, Transform, Load) pipeline that processes pet adoption data from CSV files into a PostgreSQL database, with a dashboard to monitor the process.



## What This Project Does

1. **Extract**: Reads pet data from a CSV file
2. **Transform**: Cleans and formats the data
3. **Load**: Inserts the data into a PostgreSQL database
4. **Monitor**: Shows ETL logs and database content in a dashboard

## Files in this Project

- `etl.py` - The main ETL script that processes CSV data into PostgreSQL
- `background_worker.py` - Script that runs the ETL process every 2 minutes
- `update_dashboard.py` - Creates dashboard data from logs and database
- `pet_dashboard.html` - Visual dashboard showing ETL status and pet data
- `pets.csv` / `pets_extended.csv` - Source CSV files with pet data

## How to Run the Project

### Step 1: Set up the ETL Process

```bash
# Activate your virtual environment
cd /home/dharshan/web-projects/apacheairflow-ravin
source etl/bin/activate

# Run ETL process manually once to test
python etl.py
```

### Step 2: Start the Background ETL Process

```bash
# Make the background script executable
chmod +x background_worker.py

# Run in background with nohup
nohup python background_worker.py > background.log 2>&1 &

# Check if it's running
ps aux | grep background_worker.py
```

### Step 3: Generate Dashboard Data

```bash
# Run the dashboard update script
python update_dashboard.py
```

### Step 4: View the Dashboard

Just open `pet_dashboard.html` in any web browser. Click the "Refresh Dashboard" button to see the latest data.

## How Everything Works Together

1. **CSV File** → `etl.py` → **PostgreSQL Database**
   - The ETL script reads from CSV, transforms data, and loads to database

2. **Background Worker** repeatedly runs the ETL process every 2 minutes
   - This keeps your database updated without manual intervention

3. **update_dashboard.py** collects information from:
   - Database (to show pet records)
   - Log files (to show ETL process status)
   - Creates `dashboard_data.json` file

4. **pet_dashboard.html** displays everything in a neat interface:
   - Pet records from the database
   - ETL logs showing successful runs or errors
   - Status summary and metrics

## Troubleshooting

- **No data in dashboard?** Run `python update_dashboard.py` to refresh dashboard data
- **ETL not running?** Check `ps aux | grep background_worker.py` to see if background process is running
- **Database errors?** Check connection string in `etl.py`
- **Not seeing latest CSV data?** Make sure CSV path in `etl.py` is correct

## Common Commands

```bash
# Run ETL manually
python etl.py

# Update dashboard data manually
python update_dashboard.py

# Check ETL logs
cat pet_etl.log

# Stop background process
kill $(pgrep -f "python background_worker.py")
```

---
