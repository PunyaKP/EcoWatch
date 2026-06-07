from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import requests
import boto3
from botocore.exceptions import NoCredentialsError

# AWS S3 Config
AWS_ACCESS_KEY = 'YOUR_ACCESS_KEY'
AWS_SECRET_KEY = 'YOUR_SECRET_KEY'
AWS_BUCKET = 'ecowatch-kodagu'
AWS_REGION = 'ap-south-1'

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

def upload_to_s3(file, filename):
    try:
        s3.upload_fileobj(
            file,
            AWS_BUCKET,
            filename,
            ExtraArgs={'ACL':'public-read','ContentType':file.content_type}
        )
        return f'https://{AWS_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}'
    except NoCredentialsError:
        return None

def get_real_aqi():
    API_KEY = '297160c9c000df59a7f57748764f48f6'
    url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat=12.4244&lon=75.7382&appid={API_KEY}'
    r = requests.get(url).json()
    aqi = r['list'][0]['main']['aqi']
    # 1=Good 2=Fair 3=Moderate 4=Poor 5=VeryPoor
    aqi_map = {1:15, 2:45, 3:85, 4:130, 5:180}
    return aqi_map.get(aqi, 50)

def get_real_weather():
    API_KEY = '297160c9c000df59a7f57748764f48f6'
    url = f'http://api.openweathermap.org/data/2.5/weather?lat=12.4244&lon=75.7382&appid={API_KEY}&units=metric'
    r = requests.get(url).json()
    return {
        'temp': round(r['main']['temp']),
        'humidity': r['main']['humidity'],
        'wind': round(r['wind']['speed'] * 3.6)
    }

app = Flask(__name__)
app.secret_key = 'ecowatch-secret-key-kodagu-2024'

# Upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Real users database
USERS = {
    'admin': {
        'password': 'ecowatch123',
        'name': 'Punya',
        'role': 'Administrator'
    },
    'aarav': {
        'password': 'kodagu2024',
        'name': 'Aarav Mehta',
        'role': 'Eco Warrior'
    }
}

# Seed reports data
def load_reports():
    if os.path.exists('reports.json'):
        with open('reports.json', 'r') as f:
            return json.load(f)
    return []

def save_reports():
    with open('reports.json', 'w') as f:
        json.dump(reports, f, indent=2)

reports = load_reports()  

def save_reports():
    with open('reports.json', 'w') as f:
        json.dump(reports, f, indent=2)
reports = load_reports()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_stats():
    total = len(reports)
    critical = sum(1 for r in reports if r['status'] == 'Critical')
    high = sum(1 for r in reports if r['status'] == 'High')
    medium = sum(1 for r in reports if r['status'] == 'Medium')
    low = sum(1 for r in reports if r['status'] == 'Low')
    resolved = sum(1 for r in reports if r['status'] == 'Low')
    pending = critical + high
    progress = medium
    
    categories = {
        "Air Pollution": sum(1 for r in reports if r['issue'] == 'Air Pollution'),
        "Water Pollution": sum(1 for r in reports if r['issue'] == 'Water Contamination'),
        "Waste Management": sum(1 for r in reports if 'Dump' in r['issue'] or 'Waste' in r['issue']),
        "Deforestation": sum(1 for r in reports if r['issue'] == 'Deforestation'),
        "Noise Pollution": sum(1 for r in reports if r['issue'] == 'Noise Pollution'),
    }
    
    avg_risk = int(sum(r['risk_score'] for r in reports) / len(reports)) if reports else 0
    
    return {
        'total': total,
        'critical': critical,
        'pending': pending,
        'progress': progress,
        'resolved': resolved,
        'categories': categories,
        'avg_risk': avg_risk
    }

# ── ROUTES ──────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    
    if username in USERS and USERS[username]['password'] == password:
        session['user'] = username
        session['name'] = USERS[username]['name']
        session['role'] = USERS[username]['role']
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password. Please try again.')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    stats = get_stats()
    
    return render_template(
        'index.html',
        reports=reports,
        total_user_reports=stats['total'],
        critical_count=stats['critical'],
        pending_count=stats['pending'],
        progress_count=stats['progress'],
        resolved_count=stats['resolved'],
        avg_risk=stats['avg_risk'],
        categories=stats['categories'],
        username=session.get('name'),
        role=session.get('role')
    )

@app.route('/submit-report', methods=['POST'])
def submit_report():
    if 'user' not in session:
        return redirect(url_for('login'))

    location = request.form.get('location', '')
    issue = request.form.get('issue', '')
    description = request.form.get('description', '')
    severity = request.form.get('severity', 'Medium')

    risk_map = {
        'Critical': random.randint(88, 99),
        'High': random.randint(70, 87),
        'Medium': random.randint(45, 69),
        'Low': random.randint(10, 44)
    }
    risk_score = risk_map.get(severity, 60)

    status_map = {
        'Critical': 'Critical',
        'High': 'High',
        'Medium': 'Medium',
        'Low': 'Low'
    }
    status = status_map.get(severity, 'Medium')

    img_url = ''
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo and photo.filename != '' and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(filepath)
            img_url = '/static/uploads/' + filename

    now = datetime.now().strftime('%b %d, %Y %I:%M %p')
    
    new_report = {
        "issue": issue,
        "location": location,
        "description": description,
        "risk_score": risk_score,
        "status": status,
        "time": now,
        "img": img_url
    }
    
    reports.insert(0, new_report)
    save_reports()

    return redirect(url_for('reports_page'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return app.send_static_file('../uploads/' + filename)

@app.route('/reports')
def reports_page():
    if 'user' not in session:
        return redirect(url_for('login'))
    stats = get_stats()
    return render_template('reports.html', reports=reports,
        total_user_reports=stats['total'],
        critical_count=stats['critical'],
        pending_count=stats['pending'],
        progress_count=stats['progress'],
        resolved_count=stats['resolved'],
        avg_risk=stats['avg_risk'],
        categories=stats['categories'],
        username=session.get('name'),
        role=session.get('role'))
@app.route('/analytics')
def analytics():
    if 'user' not in session:
        return redirect(url_for('login'))
    stats = get_stats()
    return render_template('analytics.html',
        username=session.get('name'),
        reports=reports,
        total_user_reports=stats['total'],
        critical_count=stats['critical'])

@app.route('/alerts')
def alerts():
    if 'user' not in session:
        return redirect(url_for('login'))
    critical_reports = [r for r in reports if r['status'] == 'Critical']
    return render_template('alerts.html',
        username=session.get('name'),
        alerts=critical_reports,
        critical_count=len(critical_reports))

@app.route('/map')
def map_view():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('map.html',
        username=session.get('name'),
        reports=reports)

@app.route('/ai')
def ai_insights():
    if 'user' not in session:
        return redirect(url_for('login'))
    stats = get_stats()
    return render_template('ai.html',
        username=session.get('name'),
        avg_risk=stats['avg_risk'],
        total_user_reports=stats['total'])

@app.route('/users')
def users():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('users.html',
        username=session.get('name'))

@app.route('/settings')
def settings():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html',
        username=session.get('name'))
@app.route('/resolve-report/<int:index>', methods=['POST'])
def resolve_report(index):
    if 'user' not in session:
        return redirect(url_for('login'))
    if 0 <= index < len(reports):
        reports.pop(index)
        save_reports()
    return redirect(url_for('reports_page'))
if __name__ == '__main__':
    app.run(debug=True)