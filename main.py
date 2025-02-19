
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from twilio.rest import Client
import requests
import os

app = Flask(__name__)
CORS(app)

# Database Configuration (SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alerts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Twilio Configuration (Replace with your credentials)
TWILIO_ACCOUNT_SID = 'your_twilio_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'

# Twitter API Configuration (Replace with your credentials)
TWITTER_BEARER_TOKEN = "your_twitter_bearer_token"
TWITTER_API_URL = "https://api.twitter.com/2/tweets"

# Alert Model
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disaster_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    impact = db.Column(db.String(255), nullable=False)
    actions = db.Column(db.String(255), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

# Send SMS Alert via Twilio
def send_sms_alert(message, phone_number):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return "SMS Sent Successfully"
    except Exception as e:
        return str(e)

# Post to Twitter
def post_to_twitter(message):
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}", "Content-Type": "application/json"}
    payload = {"text": message}
    response = requests.post(TWITTER_API_URL, headers=headers, json=payload)
    return response.json()

# Create Alert API Endpoint
@app.route('/alert', methods=['POST'])
def create_alert():
    data = request.json
    new_alert = Alert(
        disaster_type=data['disaster_type'],
        location=data['location'],
        impact=data['impact'],
        actions=data['actions']
    )
    
    db.session.add(new_alert)
    db.session.commit()

    alert_message = f"🚨 {data['disaster_type']} Alert 🚨\nLocation: {data['location']}\nImpact: {data['impact']}\nAction: {data['actions']}"

    # Send notifications
    sms_status = send_sms_alert(alert_message, '+1234567890')  # Replace with recipient phone number
    twitter_status = post_to_twitter(alert_message)

    return jsonify({
        "message": "Alert created successfully!",
        "sms_status": sms_status,
        "twitter_status": twitter_status
    }), 201

# Get Alerts API Endpoint
@app.route('/alerts', methods=['GET'])
def get_alerts():
    alerts = Alert.query.all()
    alert_list = [{
        "id": alert.id,
        "disaster_type": alert.disaster_type,
        "location": alert.location,
        "impact": alert.impact,
        "actions": alert.actions
    } for alert in alerts]
    
    return jsonify(alert_list)

if __name__ == '__main__':
    app.run(debug=True)

