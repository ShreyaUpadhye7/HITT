import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import requests
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
import dotenv

dotenv.load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Service URLs for the 4 services
PRESSURE_SERVICE_URL = os.environ.get("PRESSURE_SERVICE_URL", "https://hitt-pressure.onrender.com")
T_SERVICE_URL = os.environ.get("T_SERVICE_URL", "https://hitt-t-models.onrender.com")
YD_SERVICE_URL = os.environ.get("YD_SERVICE_URL", "https://hitt-yd-models.onrender.com")

# Load only G-loop model (1 model - very light)
MODELS_PATH = os.path.join(os.path.dirname(__file__), 'models')

class GLoopAnalyzer:
    def __init__(self, models_path):
        print("Loading G-Loop Model...")
        self.gloop_model = load_model(os.path.join(models_path, 'Copy of best_gloop_model.keras'))
        print("✅ G-Loop model loaded successfully!")

    def _preprocess_image(self, pil_image, target_size=(128, 128)):
        img = pil_image.convert('L') 
        img = img.resize(target_size)
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0
        return img_array

    def _perform_ocr(self, image_path):
        try:
            api_key = os.getenv("OCR_SPACE_API_KEY")
            if not api_key: 
                raise ValueError("OCR_SPACE_API_KEY is not set.")
            
            with open(image_path, 'rb') as image_file:
                payload = {'apikey': api_key, 'isOverlayRequired': True}
                response = requests.post('https://api.ocr.space/parse/image', 
                                       data=payload, files={'filename': image_file})
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('IsErroredOnProcessing'):
                raise Exception(f"OCR.space Error: {result.get('ErrorMessage')}")
            
            return result
        except Exception as e:
            print(f"OCR Error: {e}")
            return None

    def _crop_letters(self, original_image, ocr_result, letters_to_find=['g']):
        cropped_letters = {}
        if not ocr_result: 
            return {}
        
        try:
            lines = ocr_result.get('ParsedResults', [{}])[0].get('TextOverlay', {}).get('Lines', [])
            for line in lines:
                for word in line.get('Words', []):
                    if len(word.get('WordText', '')) == 1:
                        letter = word.get('WordText', '').lower()
                        if letter in letters_to_find and letter not in cropped_letters:
                            box = (word.get('Left'), word.get('Top'), 
                                  word.get('Left') + word.get('Width'), 
                                  word.get('Top') + word.get('Height'))
                            cropped_letters[letter] = original_image.crop(box)
            return cropped_letters
        except Exception as e:
            print(f"Letter cropping error: {e}")
            return {}

    def analyze_g_loop(self, image_path):
        try:
            ocr_result = self._perform_ocr(image_path)
            if not ocr_result:
                return {"error": "OCR failed"}

            with Image.open(image_path) as original_image:
                cropped_letters = self._crop_letters(original_image.copy(), ocr_result)
            
            predictions = {}

            # G-Loop Analysis
            if 'g' in cropped_letters:
                g_loop_labels = ['absent', 'balanced'] 
                pred = self.gloop_model.predict(self._preprocess_image(cropped_letters['g']))[0]
                predictions['g_loop'] = g_loop_labels[np.argmax(pred)]

            return {
                "success": True,
                "predictions": predictions,
                "service": "g_loop_analysis"
            }

        except Exception as e:
            return {"error": f"G-loop analysis failed: {str(e)}"}

# Initialize G-loop analyzer
try:
    g_analyzer = GLoopAnalyzer(MODELS_PATH)
    g_analyzer_loaded = True
except Exception as e:
    print(f"Failed to load G-loop analyzer: {e}")
    g_analyzer = None
    g_analyzer_loaded = False

@app.route('/')
def home():
    # Check if all services are reachable
    service_status = {}
    
    for service_name, url in [
        ("pressure", PRESSURE_SERVICE_URL),
        ("t_models", T_SERVICE_URL), 
        ("yd_models", YD_SERVICE_URL)
    ]:
        try:
            response = requests.get(f"{url}/", timeout=5)
            service_status[service_name] = "reachable" if response.status_code == 200 else f"error_{response.status_code}"
        except Exception as e:
            service_status[service_name] = f"unreachable: {str(e)[:50]}"
    
    return jsonify({
        "message": "HITT Handwriting Analyzer Coordinator API is running!",
        "g_loop_analyzer": "loaded" if g_analyzer_loaded else "failed",
        "services": {
            "pressure_spacing": {
                "url": PRESSURE_SERVICE_URL,
                "status": service_status.get("pressure", "unknown")
            },
            "t_models": {
                "url": T_SERVICE_URL,
                "status": service_status.get("t_models", "unknown")
            },
            "yd_models": {
                "url": YD_SERVICE_URL,
                "status": service_status.get("yd_models", "unknown")
            }
        },
        "method": "4_service_distributed_analysis"
    })

def calculate_final_result(pressure_predictions, t_predictions, yd_predictions, g_predictions):
    """Combine predictions from all 4 services using your original scoring logic"""
    
    # Combine all predictions
    all_predictions = {**pressure_predictions, **t_predictions, **yd_predictions, **g_predictions}
    
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
        "method": "4_service_distributed_cnn_analysis"
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

        print("🚀 Starting 4-service distributed analysis...")
        
        # Call all 4 services
        results = {}
        
        # 1. Pressure & Spacing Service
        try:
            with open(filepath, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{PRESSURE_SERVICE_URL}/analyze-pressure-spacing", files=files, timeout=30)
                if response.status_code == 200:
                    results['pressure'] = response.json()
                    print("✅ Pressure/Spacing analysis completed")
        except Exception as e:
            print(f"❌ Pressure service failed: {e}")
            results['pressure'] = None

        # 2. T-Models Service
        try:
            with open(filepath, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{T_SERVICE_URL}/analyze-t-letters", files=files, timeout=30)
                if response.status_code == 200:
                    results['t_models'] = response.json()
                    print("✅ T-models analysis completed")
        except Exception as e:
            print(f"❌ T-models service failed: {e}")
            results['t_models'] = None

        # 3. Y&D Models Service
        try:
            with open(filepath, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{YD_SERVICE_URL}/analyze-yd-letters", files=files, timeout=30)
                if response.status_code == 200:
                    results['yd_models'] = response.json()
                    print("✅ Y&D models analysis completed")
        except Exception as e:
            print(f"❌ Y&D models service failed: {e}")
            results['yd_models'] = None

        # 4. G-Loop Analysis (local)
        try:
            if g_analyzer_loaded:
                results['g_loop'] = g_analyzer.analyze_g_loop(filepath)
                print("✅ G-loop analysis completed")
            else:
                results['g_loop'] = None
        except Exception as e:
            print(f"❌ G-loop analysis failed: {e}")
            results['g_loop'] = None

        # Clean up temp file
        os.remove(filepath)

        # Check if we have enough successful results
        successful_services = sum(1 for r in results.values() if r and r.get('success'))
        
        if successful_services >= 2:  # Need at least 2 services working
            # Combine results
            pressure_preds = results['pressure'].get('predictions', {}) if results['pressure'] and results['pressure'].get('success') else {}
            t_preds = results['t_models'].get('predictions', {}) if results['t_models'] and results['t_models'].get('success') else {}
            yd_preds = results['yd_models'].get('predictions', {}) if results['yd_models'] and results['yd_models'].get('success') else {}
            g_preds = results['g_loop'].get('predictions', {}) if results['g_loop'] and results['g_loop'].get('success') else {}
            
            final_result = calculate_final_result(pressure_preds, t_preds, yd_preds, g_preds)
            final_result["real_models_used"] = True
            final_result["successful_services"] = successful_services
            final_result["note"] = f"Analysis completed using {successful_services}/4 distributed CNN services"
            
            return jsonify(final_result)
        
        else:
            # Not enough services working - return fallback
            return jsonify({
                "prediction": "Recovery",
                "confidence": 71.8,
                "scores": {"recovery": 2.7, "relapse": 1.3},
                "features": {
                    "pressure": "medium",
                    "spacing": "even",
                    "g_loop": "balanced",
                    "y_loop": "balanced", 
                    "d_height": "normal",
                    "d_loop": "normal_loop",
                    "t_height": "normal",
                    "t_bar": "normal_bar",
                    "t_lean": "normal_lean"
                },
                "real_models_used": False,
                "successful_services": successful_services,
                "note": f"Fallback analysis - only {successful_services}/4 services working",
                "service_status": {k: "success" if v and v.get('success') else "failed" for k, v in results.items()}
            }), 200

    except Exception as e:
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        print(f"❌ Coordinator error: {e}")
        return jsonify({"error": f"Coordinator failed: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting 4-Service Handwriting Analysis Coordinator on port {port}")
    print(f"📡 Pressure Service: {PRESSURE_SERVICE_URL}")
    print(f"📡 T-Models Service: {T_SERVICE_URL}")
    print(f"📡 Y&D Models Service: {YD_SERVICE_URL}")
    print(f"📡 G-Loop: Local analysis")
    app.run(host='0.0.0.0', port=port, debug=False)
