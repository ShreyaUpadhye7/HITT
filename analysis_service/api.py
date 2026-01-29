import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import requests

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Service URLs (will be updated with deployed URLs)
LETTER_SERVICE_URL = os.environ.get("LETTER_SERVICE_URL", "http://localhost:5001")
SPACING_SERVICE_URL = os.environ.get("SPACING_SERVICE_URL", "http://localhost:5002")

@app.route('/')
def home():
    return jsonify({
        "message": "HITT Handwriting Analyzer Coordinator API is running!",
        "services": {
            "letter_analysis": LETTER_SERVICE_URL,
            "spacing_analysis": SPACING_SERVICE_URL
        },
        "method": "distributed_analysis"
    })

def calculate_final_result(letter_predictions, spacing_predictions):
    """Combine predictions from both services using your original scoring logic"""
    
    # Combine all predictions
    all_predictions = {**letter_predictions, **spacing_predictions}
    
    relapse_score = 0
    recovery_score = 0
    
    # Your original scoring logic
    # Pressure (balanced) - Recovery weighted 2x
    if all_predictions.get('pressure') in ['light', 'heavy']: 
        relapse_score += 1
    elif all_predictions.get('pressure') == 'medium': 
        recovery_score += 2
    
    # Spacing (balanced) - Recovery weighted 2x
    if all_predictions.get('spacing') in ['uneven', 'very uneven']: 
        relapse_score += 1
    elif all_predictions.get('spacing') in ['even', 'very even']: 
        recovery_score += 2
    
    # G-Loop (balanced) - Recovery weighted 2x
    if all_predictions.get('g_loop') == 'absent': 
        relapse_score += 1
    elif all_predictions.get('g_loop') == 'balanced': 
        recovery_score += 2
    
    # Y-Loop (balanced) - Recovery weighted 2x
    if all_predictions.get('y_loop') == 'absent': 
        relapse_score += 1
    elif all_predictions.get('y_loop') == 'balanced': 
        recovery_score += 2
    
    # D-Height (balanced) - Recovery weighted 2x
    if all_predictions.get('d_height') == 'tall': 
        relapse_score += 1
    elif all_predictions.get('d_height') == 'normal': 
        recovery_score += 2
    
    # T-Height (balanced) - Recovery weighted 2x
    if all_predictions.get('t_height') == 'tall': 
        relapse_score += 1
    elif all_predictions.get('t_height') == 'normal': 
        recovery_score += 2
    
    # D-Loop (balanced) - Recovery weighted 2x
    if all_predictions.get('d_loop') == 'wide_loop': 
        relapse_score += 1
    elif all_predictions.get('d_loop') == 'normal_loop': 
        recovery_score += 2
    
    # T-Lean (balanced) - Recovery weighted 2x
    if all_predictions.get('t_lean') == 'left_lean': 
        relapse_score += 1
    elif all_predictions.get('t_lean') == 'normal_lean': 
        recovery_score += 2
    
    # T-Bar (balanced) - Recovery weighted 2x
    if all_predictions.get('t_bar') == 'heavy_bar': 
        recovery_score += 2
    elif all_predictions.get('t_bar') == 'normal_bar': 
        relapse_score += 1
    
    # Final prediction - Recovery wins on tie
    if relapse_score > recovery_score: 
        final_prediction = "Relapse Risk"
    else:  # Recovery wins on tie or when ahead
        final_prediction = "Recovery"
    
    print(f"🧮 Final Scoring - Recovery: {recovery_score}, Relapse: {relapse_score}, Prediction: {final_prediction}")
    
    return {
        "prediction": final_prediction, 
        "scores": {"relapse": relapse_score, "recovery": recovery_score}, 
        "features": all_predictions,
        "method": "distributed_cnn_analysis"
    }

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            file.save(tmp.name)
            filepath = tmp.name

        print("🚀 Starting distributed analysis...")
        
        # Call Letter Analysis Service
        letter_result = None
        try:
            with open(filepath, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{LETTER_SERVICE_URL}/analyze-letters", files=files, timeout=30)
                if response.status_code == 200:
                    letter_result = response.json()
                    print("✅ Letter analysis completed")
                else:
                    print(f"❌ Letter service error: {response.status_code}")
        except Exception as e:
            print(f"❌ Letter service failed: {e}")

        # Call Spacing Analysis Service  
        spacing_result = None
        try:
            with open(filepath, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{SPACING_SERVICE_URL}/analyze-spacing", files=files, timeout=30)
                if response.status_code == 200:
                    spacing_result = response.json()
                    print("✅ Spacing analysis completed")
                else:
                    print(f"❌ Spacing service error: {response.status_code}")
        except Exception as e:
            print(f"❌ Spacing service failed: {e}")

        # Clean up temp file
        os.remove(filepath)

        # Combine results
        if letter_result and letter_result.get('success') and spacing_result and spacing_result.get('success'):
            # Both services succeeded - use real CNN analysis
            final_result = calculate_final_result(
                letter_result.get('predictions', {}),
                spacing_result.get('predictions', {})
            )
            final_result["real_models_used"] = True
            final_result["note"] = "Analysis completed using your distributed CNN models"
            return jsonify(final_result)
        
        else:
            # One or both services failed - return error with details
            return jsonify({
                "error": "Distributed analysis failed",
                "letter_service": "success" if letter_result and letter_result.get('success') else "failed",
                "spacing_service": "success" if spacing_result and spacing_result.get('success') else "failed",
                "letter_error": letter_result.get('error') if letter_result else "No response",
                "spacing_error": spacing_result.get('error') if spacing_result else "No response"
            }), 500

    except Exception as e:
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        print(f"❌ Coordinator error: {e}")
        return jsonify({"error": f"Coordinator failed: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Handwriting Analysis Coordinator on port {port}")
    print(f"📡 Letter Service: {LETTER_SERVICE_URL}")
    print(f"📡 Spacing Service: {SPACING_SERVICE_URL}")
    app.run(host='0.0.0.0', port=port, debug=False)
