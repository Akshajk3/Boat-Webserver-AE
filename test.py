import time
import board
import busio
import adafruit_gps

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)

gps = adafruit_gps.GPS(uart, debug=False)

gps.send_command(b'PMTK220,1000')
gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

last_print = time.monotonic()
while True:
    gps.update()
    current = time.monotonic()
    if current - last_print >= 1.0:
        last_print = current
        if not gps.has_fix:
            print("Waiting for fix...")
            continue

        print("=" * 40)
        print(f"Fix timestamp: {gps.timestamp_utc}")
        print(f"Latitude: {gps.latitude:.6f}, Longitude: {gps.longitude:.6f}")
        print(f"Altitude: {gps.altitude_m} meters")
        print(f"Speed: {gps.speed_knots} knots")
        print(f"Track angle: {gps.track_angle_deg}")