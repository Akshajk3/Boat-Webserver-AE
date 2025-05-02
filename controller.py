import pyvesc
from pyvesc.VESC.messages import GetValues, SetRPM, SetCurrent, SetDutyCycle
import serial
import time
import serial.tools.list_ports
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def choose_serial_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
        exit(1)

    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} - {port.description}")
    choice = input("Select the port number: ")

    try:
        idx = int(choice)
        return ports[idx].device
    except (ValueError, IndexError):
        print("Invalid selection.")
        exit(1)

def get_values_example(serialport):
    with serial.Serial(serialport, baudrate=115200, timeout=0.05) as ser:
        try:
            buffer = bytearray()

            while True:
                if GPIO.input(24):
                    print("Pin 24 is HIGH")
                    ser.write(pyvesc.encode(SetRPM(3000)))
                else:
                    print("Pin 24 is LOW")
                    ser.write(pyvesc.encode(SetRPM(0)))

                ser.write(pyvesc.encode_request(GetValues))

                if ser.in_waiting:
                    buffer += ser.read(ser.in_waiting)
                    try:
                        response, consumed = pyvesc.decode(buffer)
                        buffer = buffer[consumed:]
                        if hasattr(response, 'rpm'):
                            print("RPM:", response.rpm)
                    except Exception:
                        pass

                time.sleep(0.1)

        except KeyboardInterrupt:
            ser.write(pyvesc.encode(SetCurrent(0)))
            print("\nStopped motor.")
        finally:
            GPIO.cleanup()

if __name__ == "__main__":
    port = choose_serial_port()
    get_values_example(port)
