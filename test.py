from flask import Flask, jsonify, render_template, request
from pyngrok import ngrok
import time
import threading
import serial
from serial.tools import list_ports

app = Flask(__name__)

arduino = None
motor_running = False

throttle = 0.0
mode = 'IDLE'  # default mode
lock = threading.Lock()

def read_serial():
    global motor_running
    if arduino and arduino.in_waiting > 0:
        data = arduino.readline().decode('utf-8').strip()
        if data == "Failed to get data!":
            motor_running = False
        else:
            motor_running = True

        try:
            rpm, volt, amps, power, duty, read_mode, power_source = data.split(",")
            return rpm, volt, amps, power, duty, read_mode, power_source
        except ValueError:
            print("Bad Line:", data)

    return None

@app.route('/select-port', methods=['GET', 'POST'])
def select_port():
    global arduino
    ports = list(list_ports.comports())

    if request.method == 'POST':
        selected_port = request.form['port']
        try:
            arduino = serial.Serial(port=selected_port, baudrate=9600, timeout=0.1)
            arduino.flush()
            threading.Thread(target=serial_write_loop, daemon=True).start()
            return render_template('port_selected.html', port=selected_port)
        except serial.SerialException as e:
            return f"Error: {e}", 400

    return render_template('select_port.html', ports=ports)

@app.route('/api/data')
def get_data():
    global motor_running
    data = read_serial()
    if data and motor_running:
        rpm, volt, amps, power, duty, mode_val, power_source = data
        return jsonify({
            'rpm': rpm,
            'volts': volt,
            'amps': amps,
            'power': power,
            'duty': duty,
            'mode': mode_val,
            'power_source': power_source,
            'motor_running': True,
            'timestamp': int(time.time())
        })
    else:
        return jsonify({'motor_running': False})

@app.route('/gnd')
def index():
    return render_template('ground.html')

@app.route('/')
def boat():
    return render_template('boat.html')

@app.route('/api/button', methods=['POST'])
def button_pressed():
    print("Button was pressed")
    return jsonify({'status': 'success'})

@app.route('/api/throttle', methods=['POST'])
def set_throttle():
    global throttle
    data = request.get_json()
    if not data or 'throttle' not in data:
        return jsonify({'status': 'error', 'message': 'Throttle value missing'}), 400
    with lock:
        throttle = float(data.get('throttle'))
    print(f"Throttle set to {throttle}")
    return jsonify({'status': 'success'})

@app.route('/api/mode', methods=['POST'])
def set_mode():
    global mode
    data = request.get_json()
    if not data or 'mode' not in data:
        return jsonify({'status': 'error', 'message': 'Drive mode missing'}), 400
    with lock:
        mode = str(data.get('mode')).upper()
    print(f"Drive Mode set to {mode}")
    return jsonify({'status': 'success'})

def serial_write_loop():
    global throttle, mode, arduino
    while True:
        if arduino and arduino.is_open:
            try:
                with lock:
                    msg = f"{mode}:{throttle:.2f}\n"
                arduino.write(msg.encode('utf-8'))
                time.sleep(0.1)  # send every 100ms
            except serial.SerialException as e:
                print("Serial write failed:", e)
                break
        else:
            time.sleep(1)

def start_ngrok():
    ngrok.set_auth_token('2lgsFcb8grI0o8ScngYQK6GAOJf_5JdDrnQRQx9KpPeVsp5cK')
    public_url = ngrok.connect(5000)
    print(f"Ngrok Tunnel URL: {public_url}")

if __name__ == "__main__":
    threading.Thread(target=start_ngrok, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
