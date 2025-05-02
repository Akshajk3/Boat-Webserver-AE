import pyvesc
from pyvesc.VESC.messages import GetValues, SetRPM, SetCurrent, SetRotorPositionMode, GetRotorPosition
import serial
import time
import serial.tools.list_ports

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
            # Optional: Turn on rotor position reading if an encoder is installed
            ser.write(pyvesc.encode(SetRotorPositionMode(SetRotorPositionMode.DISP_POS_MODE_ENCODER)))

            while True:
                ser.write(pyvesc.encode(SetRPM(3000)))
                ser.write(pyvesc.encode_request(GetValues))

                if ser.in_waiting > 61:
                    (response, consumed) = pyvesc.decode(ser.read(61))
                    try:
                        print("RPM:", response.rpm)
                    except AttributeError:
                        pass

                time.sleep(0.1)

        except KeyboardInterrupt:
            ser.write(pyvesc.encode(SetCurrent(0)))
            print("\nStopped motor.")

if __name__ == "__main__":
    port = choose_serial_port()
    get_values_example(port)
