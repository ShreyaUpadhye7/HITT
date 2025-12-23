import os
import json
import numpy as np
import dotenv
import requests
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2

# Loads the OCR_SPACE_API_KEY from your .env file
dotenv.load_dotenv()

# --- Initialize Flask App ---
app = Flask(__name__)
CORS(app)

# The path to your models and JSON files
# IMPORTANT: Update this path to where your models folder is located
MODELS_PATH = os.path.join(os.path.dirname(__file__), 'models') 

class HandwritingAnalyzer:
    def __init__(self, models_path):
        """
        Loads all the Keras models and the JSON threshold configurations.
        """
        print("Loading models...")
        # --- Load Keras CNN Models ---
        self.dheight_model = load_model(os.path.join(models_path, 'Copy of best_dheight_model.keras'))
        self.dloop_model = load_model(os.path.join(models_path, 'Copy of best_dloop_model.keras'))
        self.gloop_model = load_model(os.path.join(models_path, 'Copy of best_gloop_model.keras'))
        self.t_mirrored_model = load_model(os.path.join(models_path, 'Copy of best_t_mirrored_model.keras'))
        self.tloop_model = load_model(os.path.join(models_path, 'Copy of best_tloop_model.keras'))
        self.ttall_model = load_model(os.path.join(models_path, 'Copy of best_ttall_model.keras'))
        self.yloop_model = load_model(os.path.join(models_path, 'Copy of best_yloop_model.keras'))

        # --- Load JSON Thresholds ---
        with open(os.path.join(models_path, 'Copy of pressure_model.json'), 'r') as f:
            self.pressure_thresholds = json.load(f)
        with open(os.path.join(models_path, 'Copy of spacing_model.json'), 'r') as f:
            self.spacing_thresholds = json.load(f)

        print("Models loaded successfully!")

    def _predict_pressure(self, image_path):
        try:
            with Image.open(image_path) as img:
                grayscale_img = img.convert('L')
                np_img = np.array(grayscale_img)
                avg_pixel_value = np.mean(np_img)
                print(f"Average Pixel Intensity (Pressure): {avg_pixel_value}")
                if avg_pixel_value < self.pressure_thresholds['low_threshold']:
                    return 'heavy'
                elif avg_pixel_value > self.pressure_thresholds['high_threshold']:
                    return 'light'
                else:
                    return 'medium'
        except Exception as e:
            print(f"Error calculating pressure: {e}")
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
            print(f"Standard Deviation of Word Gaps (Spacing): {std_dev}")
            if std_dev < self.spacing_thresholds['very_even_thresh']:
                return 'very even'
            elif std_dev < self.spacing_thresholds['slightly_even_thresh']:
                return 'even'
            elif std_dev < self.spacing_thresholds['uneven_thresh']:
                return 'uneven'
            else:
                return 'very uneven'
        except Exception as e:
            print(f"Error calculating spacing: {e}")
            return 'even'

    def _perform_ocr(self, image_path):
        try:
            api_key = os.getenv("OCR_SPACE_API_KEY")
            if not api_key: raise ValueError("OCR_SPACE_API_KEY is not set.")
            with open(image_path, 'rb') as image_file:
                payload = {'apikey': api_key, 'isOverlayRequired': True}
                response = requests.post('https://api.ocr.space/parse/image', data=payload, files={'filename': image_file})
            response.raise_for_status()
            result = response.json()
            if result.get('IsErroredOnProcessing'):
                raise Exception(f"OCR.space Error: {result.get('ErrorMessage')}")
            return result
        except Exception as e:
            print(f"Error during OCR.space API call: {e}")
            return None

    def _crop_letters(self, original_image, ocr_result, letters_to_find=['g', 'y', 't', 'd', 'e']):
        cropped_letters = {}
        if not ocr_result: return {}
        try:
            lines = ocr_result.get('ParsedResults', [{}])[0].get('TextOverlay', {}).get('Lines', [])
            for line in lines:
                for word in line.get('Words', []):
                    if len(word.get('WordText', '')) == 1:
                        letter = word.get('WordText', '').lower()
                        if letter in letters_to_find and letter not in cropped_letters:
                            box = (word.get('Left'), word.get('Top'), word.get('Left') + word.get('Width'), word.get('Top') + word.get('Height'))
                            cropped_letters[letter] = original_image.crop(box)
            return cropped_letters
        except Exception as e:
            print(f"Error during letter cropping: {e}")
            return {}

    def _preprocess_image(self, pil_image, target_size=(128, 128)):
        """
        --- THIS FUNCTION IS NOW FIXED ---
        It resizes the image to 128x128 and ensures the correct shape.
        """
        img = pil_image.convert('L') 
        img = img.resize(target_size)
        img_array = img_to_array(img)
        # The flatten() line is removed, as the model expects a 2D image shape
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0
        return img_array

    def _predict_from_cnn_models(self, cropped_letters):
        predictions = {}

        # --- Labels based on your training ---
        if 'g' in cropped_letters:
            g_loop_labels = ['absent', 'balanced'] 
            pred = self.gloop_model.predict(self._preprocess_image(cropped_letters['g']))[0]
            predictions['g_loop'] = g_loop_labels[np.argmax(pred)]

        if 'y' in cropped_letters:
            y_loop_labels = ['absent', 'balanced']
            pred = self.yloop_model.predict(self._preprocess_image(cropped_letters['y']))[0]
            predictions['y_loop'] = y_loop_labels[np.argmax(pred)]

        if 'd' in cropped_letters:
            d_height_labels = ['normal', 'tall']
            d_loop_labels = ['normal_loop', 'wide_loop']
            img_d = self._preprocess_image(cropped_letters['d'])
            pred_height = self.dheight_model.predict(img_d)[0]
            pred_loop = self.dloop_model.predict(img_d)[0]
            predictions['d_height'] = d_height_labels[np.argmax(pred_height)]
            predictions['d_loop'] = d_loop_labels[np.argmax(pred_loop)]

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
            
        return predictions

    def _calculate_final_result(self, predictions):
        relapse_score = 0
        recovery_score = 0
        
        # Pressure (balanced) - Recovery weighted 2x
        if predictions.get('pressure') in ['light', 'heavy']: 
            relapse_score += 1
        elif predictions.get('pressure') == 'medium': 
            recovery_score += 2
        
        # Spacing (balanced) - Recovery weighted 2x
        if predictions.get('spacing') in ['uneven', 'very uneven']: 
            relapse_score += 1
        elif predictions.get('spacing') in ['even', 'very even']: 
            recovery_score += 2
        
        # G-Loop (balanced) - Recovery weighted 2x
        if predictions.get('g_loop') == 'absent': 
            relapse_score += 1
        elif predictions.get('g_loop') == 'balanced': 
            recovery_score += 2
        
        # Y-Loop (balanced) - Recovery weighted 2x
        if predictions.get('y_loop') == 'absent': 
            relapse_score += 1
        elif predictions.get('y_loop') == 'balanced': 
            recovery_score += 2
        
        # D-Height (balanced) - Recovery weighted 2x
        if predictions.get('d_height') == 'tall': 
            relapse_score += 1
        elif predictions.get('d_height') == 'normal': 
            recovery_score += 2
        
        # T-Height (balanced) - Recovery weighted 2x
        if predictions.get('t_height') == 'tall': 
            relapse_score += 1
        elif predictions.get('t_height') == 'normal': 
            recovery_score += 2
        
        # D-Loop (balanced) - Recovery weighted 2x
        if predictions.get('d_loop') == 'wide_loop': 
            relapse_score += 1
        elif predictions.get('d_loop') == 'normal_loop': 
            recovery_score += 2
        
        # T-Lean (balanced) - Recovery weighted 2x
        if predictions.get('t_lean') == 'left_lean': 
            relapse_score += 1
        elif predictions.get('t_lean') == 'normal_lean': 
            recovery_score += 2
        
        # T-Bar (balanced) - Recovery weighted 2x
        if predictions.get('t_bar') == 'heavy_bar': 
            recovery_score += 2
        elif predictions.get('t_bar') == 'normal_bar': 
            relapse_score += 1
        
        # Final prediction - Recovery wins on tie
        final_prediction = "Inconclusive"
        if relapse_score > recovery_score: 
            final_prediction = "Relapse Risk"
        else:  # Recovery wins on tie or when ahead
            final_prediction = "Recovery"
        
        print(f"Scoring - Recovery: {recovery_score:.1f}, Relapse: {relapse_score}, Prediction: {final_prediction}")
        
        return {"prediction": final_prediction, "scores": {"relapse": relapse_score, "recovery": recovery_score}, "features": predictions}

    def analyze(self, image_path):
        print(f"Analyzing {image_path}...")
        try:
            ocr_result = self._perform_ocr(image_path)
            if not ocr_result:
                return {"error": "OCR processing failed or returned no results."}

            with Image.open(image_path) as original_image:
                cropped_letters = self._crop_letters(original_image.copy(), ocr_result)
            
            cnn_predictions = self._predict_from_cnn_models(cropped_letters)
            pressure_prediction = self._predict_pressure(image_path)
            spacing_prediction = self._predict_spacing(ocr_result)

            all_predictions = {**cnn_predictions, "pressure": pressure_prediction, "spacing": spacing_prediction}
            
            final_result = self._calculate_final_result(all_predictions)
            
            print("Analysis complete.")
            return final_result
        except Exception as e:
            print(f"An error occurred during analysis: {e}")
            return {"error": f"An internal error occurred: {e}"}

# --- Initialize the Analyzer and set up the Flask route ---
analyzer = HandwritingAnalyzer(MODELS_PATH)

@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file temporarily
    file_path = os.path.join("temp", file.filename)
    if not os.path.exists("temp"):
        os.makedirs("temp")
    file.save(file_path)

    try:
        result = analyzer.analyze(file_path)
        return jsonify(result)
    finally:
        # Clean up the temporary file
        os.remove(file_path)

# --- The server run command ---
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)