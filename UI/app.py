from flask import Flask, request, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

# Store latest sensor readings
sensor_data = {
    "temperature": 0,
    "humidity": 0,
    "CH4": 0,
    "LPG": 0,
    "CO": 0,
    "Benzene": 0,
    "SO2": 0,
    "NH3": 0,
    "CO2": 0,
    "AirQuality": 0,
    "PM1": 0,
    "PM2_5": 0,
    "PM10": 0,
    "timestamp": datetime.now().strftime("%H:%M:%S")
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data", methods=["GET"])
def get_data():
    """Endpoint for webpage to fetch latest readings."""
    return jsonify(sensor_data)

@app.route("/upload", methods=["POST"])
def upload_data():
    """Endpoint for Arduino to POST sensor readings."""
    data = request.get_json()
    if data:
        # Update global sensor readings
        for key in data:
            sensor_data[key] = data[key]
        sensor_data["timestamp"] = datetime.now().strftime("%H:%M:%S")

        # Compute simple AQI (example weighted avg)
        gas_aqi = (sensor_data["CO"] + sensor_data["LPG"] + sensor_data["CH4"] + sensor_data["AirQuality"]) / 4
        pm_aqi = (sensor_data["PM2_5"] + sensor_data["PM10"]) / 2
        sensor_data["Overall_AQI"] = round((gas_aqi + pm_aqi) / 2, 2)

        print("✅ Data received:", sensor_data)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "msg": "No JSON received"}), 400

if __name__ == "__main__":
    # Run Flask on local IP, accessible to Arduino
    app.run(host="0.0.0.0", port=5000, debug=True)
