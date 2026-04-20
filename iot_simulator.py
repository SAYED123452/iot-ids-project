import random
import time
import requests
import numpy as np

API_URL = "http://127.0.0.1:5000/api/traffic"

devices = [
    {"id": "sensor_001", "type": "temperature_sensor"},
    {"id": "camera_002", "type": "security_camera"},
    {"id": "lock_003", "type": "smart_lock"},
    {"id": "plug_004", "type": "smart_plug"},
    {"id": "hub_005", "type": "gateway_hub"},
]

def generate_traffic(device_id, device_type):
    if device_type == "temperature_sensor":
        packet_size = random.randint(40, 200)
        duration = random.uniform(0.01, 0.5)
        protocol = random.choice([0, 1])
        src_port = random.randint(1024, 20000)
        dst_port = random.choice([1883, 8883])
        bytes_transferred = packet_size * random.randint(1, 5)
    elif device_type == "security_camera":
        packet_size = random.randint(500, 1400)
        duration = random.uniform(0.1, 1.0)
        protocol = 0
        src_port = random.randint(20000, 40000)
        dst_port = 443
        bytes_transferred = packet_size * random.randint(10, 50)
    elif device_type == "smart_lock":
        packet_size = random.randint(50, 300)
        duration = random.uniform(0.01, 0.2)
        protocol = random.choice([0, 1])
        src_port = random.randint(1024, 10000)
        dst_port = 443
        bytes_transferred = packet_size * random.randint(1, 3)
    else:
        packet_size = random.randint(40, 800)
        duration = random.uniform(0.01, 0.3)
        protocol = random.choice([0, 1, 2])
        src_port = random.randint(1024, 50000)
        dst_port = random.choice([80, 443, 1883])
        bytes_transferred = packet_size * random.randint(1, 10)
    
    attack = np.random.random() < 0.15
    if attack:
        attack_type = np.random.choice(['ddos', 'scan', 'malware'])
        if attack_type == 'ddos':
            packet_size = random.randint(1000, 1500)
            duration = random.uniform(0.001, 0.05)
            bytes_transferred = packet_size * random.randint(50, 200)
        elif attack_type == 'scan':
            packet_size = random.randint(40, 100)
            dst_port = random.randint(1, 65535)
            duration = random.uniform(0.001, 0.02)
        elif attack_type == 'malware':
            dst_port = 1883
            duration = random.uniform(2, 8)
            bytes_transferred = packet_size * random.randint(20, 100)
    
    return {
        "device_id": device_id,
        "device_type": device_type,
        "packet_size": packet_size,
        "duration": duration,
        "protocol_encoded": protocol,
        "src_port": src_port,
        "dst_port": dst_port,
        "bytes_transferred": bytes_transferred,
        "timestamp": time.time()
    }

print("="*50)
print("IoT Traffic Simulator")
print("="*50)
print(f"Simulating {len(devices)} devices")
print("Sending traffic to:", API_URL)
print("Press Ctrl+C to stop")
print("="*50)

while True:
    for device in devices:
        traffic = generate_traffic(device["id"], device["type"])
        try:
            response = requests.post(API_URL, json=traffic, timeout=2)
            if response.status_code == 200:
                result = response.json()
                if result.get("prediction") != 0:
                    print(f"[ALERT] {device['id']} -> {result.get('threat')} ({result.get('confidence')*100:.1f}%)")
            else:
                print(f"Error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("ERROR: Cannot connect to server. Make sure app.py is running.")
            break
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(random.uniform(0.5, 2))