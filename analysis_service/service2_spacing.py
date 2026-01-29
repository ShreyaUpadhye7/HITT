import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
import requests
import dotenv

dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)

# Load only T-letter and spacing models
MODELS_PATH = os.path.join(os.path.dirname(__file__), 'models')

class SpacingAnalyzer:
    def __init__(self, models_path):
        print("Loading T-Letter & Spacing Models...")
        self.tloop_model = load_model(os.path.join(models_path, 'Copy of best_tloop_model.keras'))
        self.ttall_model = load_model(os.path.join(models_path, 'Copy of best_ttall_model.keras'))
        self.t_mirrored_model = load_model(os.path.join(models_path, 'Copy of best_t_mirrored_model.keras'))
        
        # Load JSON thresholds
        with open(os.path.join(models_path, 'Copy of pressure_model.json'), 'r') as f:
            self.pressure_thresholds = json.load(f)
        with open(os.path.join(models_path, 'Copy of spacing_model.json'), 'r') as f:
            self.spacing_thresholds = json.load(f)
        
        print("✅ T-Letter & Spacing models loaded successfully!")

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

    def _crop_letters(self, original_image, ocr_result, letters_to_find=['t']):
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

    def analyze_spacing(self, image_path):
        try:
            ocr_result = self._perform_ocr(image_path)
            if not ocr_result:
                return {"error": "OCR failed"}

            with Image.open(image_path) as original_image:
                cropped_letters = self._crop_letters(original_image.copy(), ocr_result)
            
            predictions = {}

            # T-Letter Analysis
            if 't' in cropped_letters:
                t_height_labels = ['normal', 'tall']
                t_loop_labels = ['normal_bar', 'heavy_bar']
                t_mirrored_labels = ['normal_lean', 'left_lean']
                
                img_t = self._preprocess_image(cropped_letters['t'])
                
                pred_tall = self.ttall_model.predict(img_t)[0]
                pred_loop = self.tloop_model.predict(img_t)[0]
                pred_mirrored = self.t_mirrored_model.predict(img_t)[0]
                
                predictions['t_height'] = t_height_labels[np.argmax(pred_tall)]
                predictions['t_bar'] = t_loop_labels[np.argmax(pred_loop)]
                predictions['t_lean'] = t_mirrored_labels[np.argmax(pred_mirrored)]

            # Pressure & Spacing Analysis
            predictions['pressure'] = self._predict_pressure(image_path)
            predictions['spacing'] = self._predict_spacing(ocr_result)

            return {
                "success": True,
                "predictions": predictions,
                "service": "spacing_analysis"
            }

        except Exception as e:
            return {"error": f"Spacing analysis failed: {str(e)}"}

# Initialize analyzer
try:
    spacing_analyzer = SpacingAnalyzer(MODELS_PATH)
    analyzer_loaded = True
except Exception as e:
    print(f"Failed to load spacing analyzer: {e}")
    spacing_analyzer = None
    analyzer_loaded = False

@app.route('/')
def home():
    return jsonify({
        "message": "Spacing Analysis Service Running",
        "analyzer_loaded": analyzer_loaded,
        "models": ["t_height", "t_bar", "t_lean", "pressure", "spacing"]
    })

@app.route('/analyze-spacing', methods=['POST'])
def analyze_spacing_endpoint():
    if not analyzer_loaded:
        return jsonify({"error": "Spacing analyzer not loaded"}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            file.save(tmp.name)
            filepath = tmp.name

        result = spacing_analyzer.analyze_spacing(filepath)
        os.remove(filepath)
        
        return jsonify(result)

    except Exception as e:
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5002))
    print(f"Starting Spacing Analysis Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)