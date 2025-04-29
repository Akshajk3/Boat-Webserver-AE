from flask import Flask, jsonify, render_template
from pyngrok import ngrok
import random
import time
import threading
import serial

app = Flask(__name__)

arduino = serial.Serial(port='COM4', baudrate=9600, timeout=0.1)
arduino.flush()

motor_running = False

def read_serial():
    if arduino.in_waiting > 0:
        data = arduino.readline().decode('utf-8').strip()
        if data == "Failed to get data!":
            motor_running = False
        else:
            motor_running = True
        
        try:
            rpm, volt, amps, power, duty, mode, power_source = data.split(",")
        except ValueError:
            print("Bad Line: ", data)

    return rpm, volt, amps, power, duty, mode, power_source


@app.route('/api/data')
def get_data():
    data = read_serial()
    if motor_running:
        data = {
            'rpm' : data.rpm,
            'volts' : data.volt,
            'amps' : data.amps,
            'power': data.power,
            'duty': data.duty,
            'mode' : data.mode,
            'power_source' : data.power_source,
            'motor_running': True,
            'timestamp' : int(time.time())
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