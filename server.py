from flask import Flask, jsonify, render_template, request
from pyvesc import VESC
from pyvesc.VESC.messages import SetRPM, SetCurrent
import serial.tools.list_ports
import threading
import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Throttle input
GPIO.setup(1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   # Mode N
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   # Mode D
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   # Mode R

# Flask setup
app = Flask(__name__)

# Global state
vesc_motor = None
motor_data = {}
throttle = 0.0
mode = 'N'
lock = threading.Lock()

def choose_serial_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
        exit(1)

    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} - {port.description}")
    idx = int(input("Select the port number: "))
    return ports[idx].device

def motor_control_loop(port):
    global vesc_motor, throttle, mode, motor_data

    with VESC(port, baudrate=115200, timeout=0.05) as vesc_motor:
        try:
            while True:
                # GPIO-based drive mode
                if GPIO.input(1): mode = 'N'
                elif GPIO.input(2): mode = 'D'
                elif GPIO.input(3): mode = 'R'

                # Multiplier based on drive mode
                multiplier = {'N': 0, 'D': 1, 'R': -1}.get(mode, 0)

                # Update throttle based on pin 24 or web input
                pin_active = GPIO.input(24)
                effective_rpm = int(throttle * multiplier * 10000) if pin_active else 0

                with lock:
                    vesc_motor.set_rpm(effective_rpm)

                # Poll for RPM
                rpm = vesc_motor.get_rpm()
                motor_data = {
                    'rpm': rpm,
                    'mode': mode,
                    'throttle': throttle,
                    'motor_running': effective_rpm != 0,
                    'timestamp': int(time.time())
                }

                time.sleep(0.1)
        except KeyboardInterrupt:
            vesc_motor.set_current(0)
            print("\nStopped motor.")
        finally:
            GPIO.cleanup()

# Flask endpoints
@app.route('/')
def index():
    return render_template('boat.html')  # Replace with your own HTML

@app.route('/api/data')
def get_data():
    with lock:
        return jsonify(motor_data)

@app.route('/api/throttle', methods=['POST'])
def set_throttle():
    global throttle
    data = request.get_json()
    if not data or 'throttle' not in data:
        return jsonify({'status': 'error', 'message': 'Missing throttle'}), 400
    with lock:
        throttle = float(data['throttle'])
    return jsonify({'status': 'success', 'throttle': throttle})

@app.route('/api/mode', methods=['POST'])
def set_mode():
    global mode
    data = request.get_json()
    if not data or 'mode' not in data:
        return jsonify({'status': 'error', 'message': 'Missing mode'}), 400
    with lock:
        mode = data['mode'].upper()
    return jsonify({'status': 'success', 'mode': mode})

if __name__ == "__main__":
    selected_port = choose_serial_port()
    threading.Thread(target=motor_control_loop, args=(selected_port,), daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
