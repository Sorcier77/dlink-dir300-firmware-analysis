import serial
import time
import sys
import os

# --- CONFIGURATION ---
SERIAL_PORT = '/dev/tty.usbmodemflip_Yeh0n1'
BAUD_RATE = 57600
OUTPUT_FILE = "firmware_raw.bin"
EXPECTED_SIZE = 4194304  # 4 MB (0x400000)
# ---------------------

print(f"--- Firmware Dumper (UART) ---")
print(f"Target: {SERIAL_PORT} @ {BAUD_RATE}")

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3)
except Exception as e:
    print(f"Error opening serial port: {e}")
    sys.exit(1)

# 1. Reset buffers
ser.reset_input_buffer()
ser.write(b"\r\n")
time.sleep(1)
print("Serial connection initialized.")

# 2. Configure RAW mode (BusyBox/Linux)
# This prevents the router from converting \n to \r\n
print("Setting terminal to raw mode...")
ser.write(b"stty raw -echo\r\n")
time.sleep(0.5)

# Ensure mtd device node exists
ser.write(b"mknod /tmp/mtd0 c 90 0\r\n")
time.sleep(0.5)

# 3. Start capture
print("Sending cat command...")
ser.reset_input_buffer()
ser.write(b"cat /tmp/mtd0\r\n")

# 4. Read data
print(f"Reading {EXPECTED_SIZE} bytes...")
data_buffer = bytearray()
start_time = time.time()
last_print = time.time()

while len(data_buffer) < EXPECTED_SIZE:
    if ser.in_waiting:
        chunk = ser.read(ser.in_waiting)
        data_buffer.extend(chunk)
        start_time = time.time()  # Reset timeout counter

    if time.time() - start_time > 10:
        print("\n[!] Timeout: No data received for 10 seconds.")
        break

    if time.time() - last_print > 2:
        percent = (len(data_buffer) / EXPECTED_SIZE) * 100
        print(f"Progress: {len(data_buffer)} / {EXPECTED_SIZE} bytes ({percent:.1f}%)")
        last_print = time.time()

print(f"\nCapture finished. Total: {len(data_buffer)} bytes.")

# 5. Save to file
# Note: The file might start with the echoed 'cat' command if stty -echo failed or wasn't fast enough.
with open(OUTPUT_FILE, "wb") as f:
    f.write(data_buffer)

print(f"Saved to: {OUTPUT_FILE}")
print("Verify the file header using 'hexdump -C firmware_raw.bin | head'.")
print("If the file starts with the 'cat' command text, you will need to strip those bytes.")

ser.close()
