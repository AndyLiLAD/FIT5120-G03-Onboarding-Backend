from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)
OPENWEATHER_API_KEY = "03b2f1906e2b08f4a25ed147f8a4e1d3"

def get_uv_index(lat, lon):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url).json()
    current = response.get("current", {})
    daily = response.get("daily", [{}])[0]

    uv = current.get("uvi", 0)
    sunset_time = daily.get("sunset", 0)
    current_time = current.get("dt", 0)

    # Check if sunset within 30 minutes
    sunset_soon = (sunset_time - current_time) < 1800  # 1800 seconds = 30 minutes

    return uv, sunset_soon

def get_lat_lon(postcode):
    url = f"https://api.openweathermap.org/geo/1.0/zip?zip={postcode},AU&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url).json()
    return response.get("lat"), response.get("lon")

# Get UV Index by User Location
@app.route('/api/uv-index-location', methods=['POST'])
def fetch_uv_index_location():
    data = request.json
    lat = data.get("lat")
    lon = data.get("lon")

    print(f"Received location request: lat={lat}, lon={lon}")
    if lat is None or lon is None:
        print("Error: Invalid coordinates")
        return jsonify({"error": "Invalid coordinates"}), 400

    uv_index = get_uv_index(lat, lon)
    print(f"Returning UV Index: {uv_index}")
    return jsonify({"lat": lat, "lon": lon, "uv_index": uv_index})

@app.route('/api/uv-index', methods=['POST'])
def fetch_uv_index():
    try:
        postcode = request.json.get("postcode")
        lat, lon = get_lat_lon(postcode)
        if not lat or not lon:
            raise ValueError("Invalid postcode")
        uv = get_uv_index(lat, lon)
        return jsonify({"uv_index": uv})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)