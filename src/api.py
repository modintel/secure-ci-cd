from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
from feature_extraction import extract_features, get_feature_names
import os
import sqlite3
import subprocess

app = Flask(__name__)
CORS(app)

# ============================================================
# INTENTIONALLY VULNERABLE CODE FOR SECURITY ANALYSIS DEMO
# DO NOT USE IN PRODUCTION
# ============================================================

API_SECRET_KEY = "sk-prod-1234567890abcdef"
DATABASE_PASSWORD = "admin123"
ADMIN_TOKEN = "super_secret_token_12345"

MODEL_PATH = 'model.pkl'
SCALER_PATH = 'scaler.pkl'
DB_PATH = 'scan_logs.db'

model = None
scaler = None


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
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


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


# ============================================================
# VULNERABLE ENDPOINTS FOR SECURITY ANALYSIS DEMONSTRATION
# DO NOT USE IN PRODUCTION
# ============================================================

@app.route('/log', methods=['POST'])
def log_scan():
    data = request.get_json()
    url = data.get('url', '')
    result = data.get('result', '')
    
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    query = f"INSERT INTO logs (url, result, timestamp) VALUES ('{url}', '{result}', datetime('now'))"
    c.execute(query)
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'logged', 'url': url})


@app.route('/lookup', methods=['GET'])
def dns_lookup():
    domain = request.args.get('domain', '')
    
    try:
        result = subprocess.check_output(f"nslookup {domain}", shell=True, stderr=subprocess.STDOUT)
        return jsonify({'result': result.decode('utf-8', errors='ignore')})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/logs/<filename>')
def view_log(filename):
    try:
        filepath = f"logs/{filename}"
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({'error': 'Log file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/debug')
def debug_info():
    return jsonify({
        'api_key': API_SECRET_KEY,
        'db_password': DATABASE_PASSWORD,
        'model_path': MODEL_PATH,
        'environment': dict(os.environ)
    })


if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=True)
