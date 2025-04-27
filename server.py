from flask import Flask, jsonify, render_template
from pyngrok import ngrok
import random
import time
import threading

app = Flask(__name__)

@app.route('/api/data')
def get_data():
    data = {
        'temp' : round(20 + random.random() * 10, 2),
        'humidity' : round(50 + random.random() * 20, 2),
        'timestamp' : int(time.time()),
        'speed': round(random.random() * 30, 2)
    }
    return jsonify(data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/button', methods=['POST'])
def button_pressed():
    print("Button was pressed")
    return jsonify({'status' : 'success'})

def start_ngrok():
    ngrok.set_auth_token('2lgsFcb8grI0o8ScngYQK6GAOJf_5JdDrnQRQx9KpPeVsp5cK')
    public_url = ngrok.connect(5000)
    print(f"Ngrok Tunnel URL: {public_url}")

if __name__ == "__main__":
    threading.Thread(target=start_ngrok).start()
    app.run(host='0.0.0.0', port=5000)