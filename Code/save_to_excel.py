import serial
import time
import serial.tools.list_ports
import pandas as pd
from datetime import datetime
import os

# === SETTINGS ===
BAUD = 9600
EXCEL_FILE = "sensor_data.xlsx"

# === AUTO-DETECT ARDUINO PORT ===
def find_arduino():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "Arduino" in p.description or "CH340" in p.description or "USB-SERIAL" in p.description:
            print(f"✅ Arduino found on {p.device}")
            return p.device
    print("⚠️ No Arduino detected. Please check USB connection.")
    return None

# === INITIALIZE SERIAL ===
port = find_arduino()
if not port:
    exit()

try:
    ser = serial.Serial(port, BAUD, timeout=2)
    print(f"✅ Connected to {port}. Logging data to {EXCEL_FILE} ...")
    time.sleep(2)  # give time for Arduino to reset
except serial.SerialException as e:
    print(f"❌ Could not open {port}: {e}")
    exit()

# === CREATE EXCEL FILE IF NOT EXISTS ===
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=[
        "Timestamp", "Time(s)", "Temp", "Humidity",
        "CH4", "LPG", "CO", "AirQ",
        "Benzene", "SO2", "NH3", "CO2",
        "PM1", "PM2_5", "PM10"
    ])
    df.to_excel(EXCEL_FILE, index=False)

# === MAIN LOOP ===
buffer = []  # temporary in-memory storage

try:
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if not line or line.startswith("time"):
            continue  # skip header or empty lines

        parts = line.split(",")
        if len(parts) == 14:
            try:
                data = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Time(s)": float(parts[0]),
                    "Temp": float(parts[1]),
                    "Humidity": float(parts[2]),
                    "CH4": float(parts[3]),
                    "LPG": float(parts[4]),
                    "CO": float(parts[5]),
                    "AirQ": float(parts[6]),
                    "Benzene": float(parts[7]),
                    "SO2": float(parts[8]),
                    "NH3": float(parts[9]),
                    "CO2": float(parts[10]),
                    "PM1": float(parts[11]),
                    "PM2_5": float(parts[12]),
                    "PM10": float(parts[13])
                }
                buffer.append(data)
                print("✅ Logged:", data)

                # Save every 10 readings
                if len(buffer) >= 10:
                    old_df = pd.read_excel(EXCEL_FILE)
                    new_df = pd.concat([old_df, pd.DataFrame(buffer)], ignore_index=True)
                    new_df.to_excel(EXCEL_FILE, index=False)
                    buffer.clear()
                    print("💾 Data saved to Excel.\n")

            except ValueError:
                print("⚠️ Invalid numeric value received, skipping...")

except KeyboardInterrupt:
    print("\n🛑 Logging stopped by user.")
    # Save any remaining data before exit
    if buffer:
        old_df = pd.read_excel(EXCEL_FILE)
        new_df = pd.concat([old_df, pd.DataFrame(buffer)], ignore_index=True)
        new_df.to_excel(EXCEL_FILE, index=False)
        print("💾 Final data saved before exit.")
    ser.close()
