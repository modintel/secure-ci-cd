from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import joblib
import pandas as pd
from feature_extraction import extract_features, get_feature_names
import os
import sqlite3
import socket
import re

app = Flask(__name__)

CORS(app, origins=['http://localhost:3000', 'chrome-extension://*'])

MODEL_PATH = 'model.pkl'
SCALER_PATH = 'scaler.pkl'
DB_PATH = 'scan_logs.db'
LOGS_DIR = 'logs'

model = None
scaler = None


def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=()'
    return response


@app.after_request
def apply_security_headers(response):
    return add_security_headers(response)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY, url TEXT, result TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()


def load_model_and_scaler():
    global model, scaler
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            print("Model loaded successfully.")
        else:
            print(f"Model not found at {MODEL_PATH}.")
            return False
            
        if os.path.exists(SCALER_PATH):
            scaler = joblib.load(SCALER_PATH)
            print("Scaler loaded successfully.")
        else:
            print(f"Scaler not found at {SCALER_PATH}. Using unscaled features.")
            scaler = None
            
        return True
    except Exception as e:
        print(f"Error loading model/scaler: {e}")
        return False


load_model_and_scaler()


def reload_if_needed():
    global model, scaler
    if model is not None:
        return True
    return load_model_and_scaler()


@app.route('/predict', methods=['POST'])
def predict():
    if not reload_if_needed():
        return jsonify({'error': 'Model is currently training/loading. Please wait a moment and try again.'}), 503

    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400

    url = data['url']
    
    try:
        features = extract_features(url)
        features_df = pd.DataFrame([features], columns=get_feature_names())
        
        if scaler is not None:
            features_scaled = scaler.transform(features_df)
        else:
            features_scaled = features_df.values
        
        prediction = model.predict(features_scaled)[0]
        probs = model.predict_proba(features_scaled)[0]
        
        phishing_prob = probs[1] if len(probs) > 1 else probs[0]
        
        result = "PHISHING" if prediction == 1 else "LEGITIMATE"
        confidence = probs[prediction]
        
        return jsonify({
            'url': url,
            'result': result,
            'probability': float(confidence),
            'phishing_score': float(phishing_prob)
        })
        
    except Exception as e:
        return jsonify({'error': 'An error occurred processing your request'}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok', 
        'model_loaded': model is not None,
        'scaler_loaded': scaler is not None
    })


@app.route('/reload', methods=['POST'])
def reload():
    global model, scaler
    model = None
    scaler = None
    success = load_model_and_scaler()
    return jsonify({'success': success})


@app.route('/log', methods=['POST'])
def log_scan():
    data = request.get_json()
    url = data.get('url', '')
    result = data.get('result', '')
    
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute(
        "INSERT INTO logs (url, result, timestamp) VALUES (?, ?, datetime('now'))",
        (url, result)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'logged', 'url': url})


def is_valid_domain(domain):
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
    return bool(re.match(pattern, domain))


@app.route('/lookup', methods=['GET'])
def dns_lookup():
    domain = request.args.get('domain', '')
    
    if not domain or not is_valid_domain(domain):
        return jsonify({'error': 'Invalid domain format'}), 400
    
    try:
        ip_address = socket.gethostbyname(domain)
        return jsonify({
            'domain': domain,
            'ip_address': ip_address
        })
    except socket.gaierror:
        return jsonify({'error': 'Domain not found'}), 404
    except Exception:
        return jsonify({'error': 'Lookup failed'}), 500


@app.route('/logs/<filename>')
def view_log(filename):
    safe_filename = os.path.basename(filename)
    
    if not safe_filename or '..' in filename or filename.startswith('/'):
        return jsonify({'error': 'Invalid filename'}), 400
    
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    
    filepath = os.path.join(LOGS_DIR, safe_filename)
    
    real_path = os.path.realpath(filepath)
    logs_real_path = os.path.realpath(LOGS_DIR)
    
    if not real_path.startswith(logs_real_path):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({'error': 'Log file not found'}), 404
    except Exception:
        return jsonify({'error': 'Unable to read file'}), 500




if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)
