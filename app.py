import requests
import time
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mail import Mail, Message

app = Flask(__name__)
CORS(app)

# OpenWeather API Key
OPENWEATHER_API_KEY = "03b2f1906e2b08f4a25ed147f8a4e1d3"  # Replace with your API key

# Flask-Mail Configuration (Use your email provider's SMTP settings)
app.config['MAIL_SERVER'] = 'alii0071@student.monash.edu'  # Example: Gmail
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "alii0071@student.monash.edu"
app.config['MAIL_PASSWORD'] = "yourcousinlikesme"
app.config['MAIL_DEFAULT_SENDER'] = "alii0071@student.monash.edu"

mail = Mail(app)

# Get UV Index from OpenWeather
def get_uv_index(lat, lon):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    print(f"Fetching UV Index: {url}")
    response = requests.get(url).json()
    print(f"One Call API Response: {response}")
    return response.get("current", {}).get("uvi", "N/A")

# Determine recommended sunscreen reapplication time
def get_sunscreen_time(uv_index):
    if uv_index < 3:
        return 120  # 2 hours
    if uv_index < 6:
        return 90   # 1.5 hours
    if uv_index < 8:
        return 60   # 1 hour
    if uv_index < 11:
        return 45   # 45 minutes
    return 30       # 30 minutes for extreme UV

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

# Set Sunscreen Reminder & Email Notification
@app.route('/api/set-reminder', methods=['POST'])
def set_reminder():
    data = request.json
    email = data.get("email")
    uv_index = data.get("uv_index")

    print(f"Received reminder request for {email} with UV index {uv_index}")

    if not email or uv_index is None:
        print("Error: Missing email or UV index")
        return jsonify({"error": "Missing email or UV index"}), 400

    time_to_remind = get_sunscreen_time(uv_index)

    # Send an initial email confirmation
    send_email(email, f"Your sunscreen reminder is set! Reapply in {time_to_remind} minutes.")

    # Run a background thread to send the reminder email after the countdown
    threading.Thread(target=delayed_email, args=(email, time_to_remind)).start()

    print(f"Reminder set for {time_to_remind} minutes")
    return jsonify({"message": f"Reminder set for {time_to_remind} minutes.", "time": time_to_remind})

# Convert postcode to latitude & longitude
def get_lat_lon(postcode):
    url = f"https://api.openweathermap.org/geo/1.0/zip?zip={postcode},AU&appid={OPENWEATHER_API_KEY}"
    print(f"Fetching lat/lon for postcode {postcode}: {url}")
    response = requests.get(url).json()
    print(f"Geocoding API Response: {response}")

    if "lat" in response and "lon" in response:
        return response["lat"], response["lon"]

    return None, None

# Get UV Index by Postcode
@app.route('/api/uv-index', methods=['POST'])
def fetch_uv_index():
    data = request.json
    postcode = data.get("postcode")

    lat, lon = get_lat_lon(postcode)
    if lat is None or lon is None:
        return jsonify({"error": "Invalid postcode"}), 400

    uv_index = get_uv_index(lat, lon)
    return jsonify({"postcode": postcode, "uv_index": uv_index})

# Function to send email
def send_email(to_email, message):
    try:
        msg = Message("Sunscreen Reminder", recipients=[to_email])
        msg.body = message
        mail.send(msg)
        print(f"Email sent to {to_email}: {message}")
    except Exception as e:
        print(f"Email sending failed: {e}")

# Function to delay email sending
def delayed_email(email, delay_minutes):
    time.sleep(delay_minutes * 60)
    send_email(email, "Time to reapply your sunscreen!")

if __name__ == '__main__':
    app.run(debug=True, port=5000)