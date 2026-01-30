import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import json
import numpy as np
from PIL import Image
import requests
import dotenv

dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)

# Load only JSON threshold files (very lightweight)
MODELS_PATH = os.path.join(os.path.dirname(__file__), 'models')

class PressureSpacingAnalyzer:
    def __init__(self, models_path):
        print("Loading Pressure & Spacing JSON files...")
        
        # Load JSON thresholds (very small files)
        with open(os.path.join(models_path, 'Copy of pressure_model.json'), 'r') as f:
            self.pressure_thresholds = json.load(f)
        with open(os.path.join(models_path, 'Copy of spacing_model.json'), 'r') as f:
            self.spacing_thresholds = json.load(f)
        
        print("✅ Pressure & Spacing thresholds loaded successfully!")

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

    def _predict_pressure(self, image_path):
        try:
            with Image.open(image_path) as img:
                grayscale_img = img.convert('L')
                np_img = np.array(grayscale_img)
                avg_pixel_value = np.mean(np_img)
                
                if avg_pixel_value < self.pressure_thresholds['low_threshold']:
                    return 'heavy'
                elif avg_pixel_value > self.pressure_thresholds['high_threshold']:
                    return 'light'
                else:
                    return 'medium'
        except Exception as e:
            print(f"Pressure prediction error: {e}")
            return 'medium'

    def _predict_spacing(self, ocr_result):
        try:
            word_gaps = []
            lines = ocr_result.get('ParsedResults', [{}])[0].get('TextOverlay', {}).get('Lines', [])
            
            for line in lines:
                words = sorted(line.get('Words', []), key=lambda w: w['Left'])
                for i in range(len(words) - 1):
                    current_word = words[i]
                    next_word = words[i+1]
                    gap = next_word['Left'] - (current_word['Left'] + current_word['Width'])
                    if gap > 0:
                        word_gaps.append(gap)
            
            if len(word_gaps) < 2:
                return 'very even'
            
            std_dev = np.std(word_gaps)
            
            if std_dev < self.spacing_thresholds['very_even_thresh']:
                return 'very even'
            elif std_dev < self.spacing_thresholds['slightly_even_thresh']:
                return 'even'
            elif std_dev < self.spacing_thresholds['uneven_thresh']:
                return 'uneven'
            else:
                return 'very uneven'
        except Exception as e:
            print(f"Spacing prediction error: {e}")
            return 'even'

    def analyze_pressure_spacing(self, image_path):
        try:
            ocr_result = self._perform_ocr(image_path)
            if not ocr_result:
                return {"error": "OCR failed"}

            predictions = {}
            
            # Pressure & Spacing Analysis (no ML models, just calculations)
            predictions['pressure'] = self._predict_pressure(image_path)
            predictions['spacing'] = self._predict_spacing(ocr_result)

            return {
                "success": True,
                "predictions": predictions,
                "service": "pressure_spacing_analysis"
            }

        except Exception as e:
            return {"error": f"Pressure/Spacing analysis failed: {str(e)}"}

# Initialize analyzer
try:
    pressure_analyzer = PressureSpacingAnalyzer(MODELS_PATH)
    analyzer_loaded = True
except Exception as e:
    print(f"Failed to load pressure analyzer: {e}")
    pressure_analyzer = None
    analyzer_loaded = False

@app.route('/')
def home():
    return jsonify({
        "message": "Pressure & Spacing Analysis Service Running",
        "analyzer_loaded": analyzer_loaded,
        "models": ["pressure", "spacing"],
        "memory_usage": "very_low"
    })

@app.route('/analyze-pressure-spacing', methods=['POST'])
def analyze_pressure_spacing_endpoint():
    if not analyzer_loaded:
        return jsonify({"error": "Pressure analyzer not loaded"}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            file.save(tmp.name)
            filepath = tmp.name

        result = pressure_analyzer.analyze_pressure_spacing(filepath)
        os.remove(filepath)
        
        return jsonify(result)

    except Exception as e:
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Pressure & Spacing Analysis Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)