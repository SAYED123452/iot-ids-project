import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

def generate_synthetic_iot_data(n_samples=20000):
    np.random.seed(42)
    packet_size = np.random.randint(40, 1500, n_samples)
    duration = np.random.uniform(0.001, 10, n_samples)
    protocol_encoded = np.random.choice([0, 1, 2], n_samples)
    src_port = np.random.randint(1024, 65535, n_samples)
    dst_port = np.random.choice([80, 443, 1883, 8883, 53, 22], n_samples)
    bytes_transferred = packet_size * np.random.randint(1, 50, n_samples)
    
    labels = np.zeros(n_samples, dtype=int)
    ddos_mask = (packet_size > 1000) & (duration < 0.1) & (bytes_transferred > 50000)
    labels[ddos_mask] = 1
    scan_mask = (packet_size < 100) & (np.random.random(n_samples) < 0.3)
    labels[scan_mask] = 2
    malware_mask = (dst_port == 1883) & (duration > 1)
    labels[malware_mask] = 3
    random_attack = np.random.random(n_samples) < 0.05
    labels[random_attack] = np.random.choice([1,2,3], np.sum(random_attack))
    
    X = np.column_stack([packet_size, duration, protocol_encoded, src_port, dst_port, bytes_transferred])
    y = labels
    return X, y

print("Generating dataset...")
X, y = generate_synthetic_iot_data(20000)
print(f"Benign: {np.sum(y==0)}, DDoS: {np.sum(y==1)}, Scanning: {np.sum(y==2)}, Malware: {np.sum(y==3)}")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training Random Forest...")
model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print(classification_report(y_test, y_pred, target_names=['Benign', 'DDoS', 'Scanning', 'Malware']))

joblib.dump(model, 'ids_model.pkl')
print("Model saved as ids_model.pkl")