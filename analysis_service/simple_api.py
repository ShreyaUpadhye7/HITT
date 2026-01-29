import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        "message": "HITT Simple API is running!",
        "port": os.environ.get("PORT", "5000"),
        "status": "working"
    })

@app.route('/analyze', methods=['POST'])
def analyze_image():
    return jsonify({
        "prediction": "Recovery",
        "confidence": 75.5,
        "scores": {"recovery": 3, "relapse": 1},
        "features": {"pressure": "medium", "spacing": "even"},
        "note": "This is a mock response - full AI analysis not available"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Simple Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)