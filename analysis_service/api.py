import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from analyzer import HandwritingAnalyzer

# Initialize Flask app
app = Flask(__name__)

# --- Configuration ---
CORS(app)  # Allows frontend communication
UPLOAD_FOLDER = 'temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Load Analyzer once on startup ---
print("Initializing the handwriting analyzer...")
MODELS_PATH = os.path.join(os.path.dirname(__file__), 'models')

try:
    handwriting_analyzer = HandwritingAnalyzer(MODELS_PATH)
    print("Analyzer initialized successfully.")
except Exception as e:
    print(f"FATAL: Could not initialize HandwritingAnalyzer. Error: {e}")
    handwriting_analyzer = None


@app.route('/')
def home():
    return jsonify({"message": "HITT Handwriting Analyzer API is running!"})


@app.route('/analyze', methods=['POST'])
def analyze_image():
    if handwriting_analyzer is None:
        return jsonify({"error": "Analyzer initialization failed."}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Run analysis
        result = handwriting_analyzer.analyze(filepath)

        # Delete temp file
        os.remove(filepath)

        return jsonify(result)

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        print(f"Error during analysis: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Render will use this port automatically
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
