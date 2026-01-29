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

handwriting_analyzer = None
analyzer_error = None

try:
    print(f"Looking for models in: {MODELS_PATH}")
    print(f"Models directory exists: {os.path.exists(MODELS_PATH)}")
    if os.path.exists(MODELS_PATH):
        print(f"Files in models directory: {os.listdir(MODELS_PATH)}")
    
    handwriting_analyzer = HandwritingAnalyzer(MODELS_PATH)
    print("Analyzer initialized successfully.")
except Exception as e:
    analyzer_error = str(e)
    print(f"FATAL: Could not initialize HandwritingAnalyzer. Error: {e}")
    handwriting_analyzer = None


@app.route('/')
def home():
    status = {
        "message": "HITT Handwriting Analyzer API is running!",
        "analyzer_status": "initialized" if handwriting_analyzer else "failed",
        "models_path": MODELS_PATH,
        "models_exist": os.path.exists(MODELS_PATH)
    }
    if analyzer_error:
        status["error"] = analyzer_error
    if os.path.exists(MODELS_PATH):
        status["model_files"] = os.listdir(MODELS_PATH)
    return jsonify(status)


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
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
