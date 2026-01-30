import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
import requests
import dotenv
import gc
import tensorflow as tf

dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)

# Load only Y and D models (3 models)
MODELS_PATH = os.path.join(os.path.dirname(__file__), 'models')

class YDLetterAnalyzer:
    def __init__(self, models_path):
        print("Loading Y & D Letter Models...")
        self.yloop_model = load_model(os.path.join(models_path, 'Copy of best_yloop_model.keras'))
        self.dheight_model = load_model(os.path.join(models_path, 'Copy of best_dheight_model.keras'))
        self.dloop_model = load_model(os.path.join(models_path, 'Copy of best_dloop_model.keras'))
        print("✅ Y & D Letter models loaded successfully!")

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

    def _crop_letters(self, original_image, ocr_result, letters_to_find=['y', 'd']):
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

    def analyze_yd_letters(self, image_path):
        try:
            ocr_result = self._perform_ocr(image_path)
            if not ocr_result:
                return {"error": "OCR failed"}

            with Image.open(image_path) as original_image:
                cropped_letters = self._crop_letters(original_image.copy(), ocr_result)
            
            predictions = {}

            # Y-Loop Analysis
            if 'y' in cropped_letters:
                y_loop_labels = ['absent', 'balanced']
                pred = self.yloop_model.predict(self._preprocess_image(cropped_letters['y']))[0]
                predictions['y_loop'] = y_loop_labels[np.argmax(pred)]

            # D-Letter Analysis
            if 'd' in cropped_letters:
                d_height_labels = ['normal', 'tall']
                d_loop_labels = ['normal_loop', 'wide_loop']
                img_d = self._preprocess_image(cropped_letters['d'])
                
                pred_height = self.dheight_model.predict(img_d)[0]
                pred_loop = self.dloop_model.predict(img_d)[0]
                
                predictions['d_height'] = d_height_labels[np.argmax(pred_height)]
                predictions['d_loop'] = d_loop_labels[np.argmax(pred_loop)]
                
                # Memory cleanup after predictions
                tf.keras.backend.clear_session()
                gc.collect()

            return {
                "success": True,
                "predictions": predictions,
                "service": "yd_letter_analysis"
            }

        except Exception as e:
            return {"error": f"Y/D letter analysis failed: {str(e)}"}

# Initialize analyzer
try:
    yd_analyzer = YDLetterAnalyzer(MODELS_PATH)
    analyzer_loaded = True
except Exception as e:
    print(f"Failed to load Y/D letter analyzer: {e}")
    yd_analyzer = None
    analyzer_loaded = False

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "yd_models",
        "analyzer_loaded": analyzer_loaded,
        "models": ["y_loop", "d_height", "d_loop"]
    })

@app.route('/ping')
def ping():
    return jsonify({"status": "alive", "service": "yd_models"})

@app.route('/')
def home():
    return jsonify({
        "message": "Y & D Letter Analysis Service Running",
        "analyzer_loaded": analyzer_loaded,
        "models": ["y_loop", "d_height", "d_loop"],
        "memory_usage": "medium"
    })

@app.route('/analyze-yd-letters', methods=['POST'])
def analyze_yd_letters_endpoint():
    if not analyzer_loaded:
        return jsonify({"error": "Y/D letter analyzer not loaded"}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            file.save(tmp.name)
            filepath = tmp.name

        result = yd_analyzer.analyze_yd_letters(filepath)
        os.remove(filepath)
        
        return jsonify(result)

    except Exception as e:
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Y & D Letter Analysis Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)