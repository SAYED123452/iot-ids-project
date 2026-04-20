from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import numpy as np
from collections import deque
import time
import os

app = Flask(__name__)
CORS(app)

if not os.path.exists('ids_model.pkl'):
    print("ERROR: ids_model.pkl not found. Run python train_model.py first")
    exit(1)

model = joblib.load('ids_model.pkl')

alerts = deque(maxlen=100)
traffic_log = deque(maxlen=1000)

threat_names = {0: "Benign", 1: "DDoS Attack", 2: "Port Scanning", 3: "Malware C&C"}

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/traffic', methods=['POST'])
def analyze_traffic():
    try:
        data = request.get_json()
        
        features = np.array([[
            data['packet_size'],
            data['duration'],
            data['protocol_encoded'],
            data['src_port'],
            data['dst_port'],
            data['bytes_transferred']
        ]])
        
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = float(max(probabilities))
        
        traffic_log.append({
            'device': data['device_id'],
            'prediction': int(prediction),
            'confidence': confidence,
            'timestamp': data.get('timestamp', time.time())
        })
        
        if prediction != 0:
            alerts.appendleft({
                'device': data['device_id'],
                'threat': threat_names[prediction],
                'confidence': confidence,
                'timestamp': time.time()
            })
        
        return jsonify({
            'prediction': int(prediction),
            'threat': threat_names[prediction],
            'confidence': confidence,
            'status': 'alert' if prediction != 0 else 'normal'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    return jsonify(list(alerts))

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total = len(traffic_log)
    attacks = sum(1 for t in traffic_log if t['prediction'] != 0)
    return jsonify({
        'total_packets': total,
        'attacks_detected': attacks,
        'alerts_count': len(alerts)
    })

if __name__ == '__main__':
    print("="*50)
    print("IoT Intrusion Detection System")
    print("="*50)
    print("Server running at: http://localhost:5000")
    print("Make sure to run iot_simulator.py in another terminal")
    print("="*50)
    app.run(debug=True, host='127.0.0.1', port=5000)