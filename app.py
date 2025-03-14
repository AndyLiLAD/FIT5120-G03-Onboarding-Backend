import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OPENWEATHER_API_KEY = "03b2f1906e2b08f4a25ed147f8a4e1d3"  # Replace with your actual API key

# Convert postcode to latitude & longitude
def get_lat_lon(postcode):
    url = f"https://api.openweathermap.org/geo/1.0/zip?zip={postcode},AU&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url).json()

    print("Geocoding API Response:", response)  # Debugging output

    if "lat" in response and "lon" in response:
        return response["lat"], response["lon"]

    return None, None

# Fetch UV Index from OpenWeather One Call API 3.0
def get_uv_index(lat, lon):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url).json()

    print("One Call API Response:", response)  # Debugging output

    return response.get("current", {}).get("uvi", "N/A")

@app.route('/api/uv-index', methods=['POST'])
def fetch_uv_index():
    data = request.json
    postcode = data.get("postcode")

    lat, lon = get_lat_lon(postcode)
    if lat is None or lon is None:
        return jsonify({"error": "Invalid postcode"}), 400

    uv_index = get_uv_index(lat, lon)
    return jsonify({"postcode": postcode, "uv_index": uv_index})

# NEW API: Fetch UV Index using Latitude & Longitude
@app.route('/api/uv-index-location', methods=['POST'])
def fetch_uv_index_location():
    data = request.json
    lat = data.get("lat")
    lon = data.get("lon")

    if lat is None or lon is None:
        return jsonify({"error": "Invalid coordinates"}), 400

    uv_index = get_uv_index(lat, lon)
    return jsonify({"lat": lat, "lon": lon, "uv_index": uv_index})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
