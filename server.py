from flask import Flask, jsonify, render_template
from pyngrok import ngrok
import random
import time
import threading
import serial

app = Flask(__name__)

arduino = serial.Serial(port='COM4', baudrate=9600, timeout=0.1)

motor_running = False

def read_serial():
    data = arduino.readline()
    if data == "Failed to get data!":
        motor_running = False
    else:
        motor_running = True
    
    

@app.route('/api/data')
def get_data():
    if motor_running:
        data = {
            'temp' : round(20 + random.random() * 10, 2),
            'humidity' : round(50 + random.random() * 20, 2),
            'timestamp' : int(time.time()),
            'speed': round(random.random() * 30, 2),
            'motor_running': True
        }
    else:
        data = {
            'motor_running' : False
        }
    return jsonify(data)

@app.route('/gnd')
def index():
    return render_template('ground.html')

@app.route('/')
def boat():
    return render_template('boat.html')

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