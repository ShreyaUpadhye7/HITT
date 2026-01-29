import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile

# Initialize Flask app FIRST
app = Flask(__name__)
CORS(app)

# Basic configuration
UPLOAD_FOLDER = 'temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global variables for analyzer
handwriting_analyzer = None
analyzer_error = None
MODELS_PATH = os.path.join(os.path.dirname(__file__), 'models')

@app.route('/')
def home():
    status = {
        "message": "HITT Handwriting Analyzer API is running!",
        "analyzer_status": "initialized" if handwriting_analyzer else "failed",
        "models_path": MODELS_PATH,
        "models_exist": os.path.exists(MODELS_PATH),
        "port": os.environ.get("PORT", "5000")
    }
    if analyzer_error:
        status["error"] = analyzer_error
    if os.path.exists(MODELS_PATH):
        try:
            status["model_files"] = os.listdir(MODELS_PATH)
        except Exception as e:
            status["model_files_error"] = str(e)
    return jsonify(status)

@app.route('/analyze', methods=['POST'])
def analyze_image():
    # Force model loading attempt if not already loaded
    if handwriting_analyzer is None:
        print("🔄 Attempting to load models on-demand...")
        load_analyzer()
    
    if handwriting_analyzer is None:
        return jsonify({
            "error": "REAL MODELS FAILED TO LOAD", 
            "details": analyzer_error or "Models not loaded",
            "models_path": MODELS_PATH,
            "models_exist": os.path.exists(MODELS_PATH),
            "model_files": os.listdir(MODELS_PATH) if os.path.exists(MODELS_PATH) else [],
            "note": "This is a FALLBACK response - your trained models are not working"
        }), 500  # Return error so you know models failed

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        # Save file temporarily using tempfile (Render-safe)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            file.save(tmp.name)
            filepath = tmp.name

        print(f"🧠 Using REAL AI models to analyze: {filepath}")
        # Run analysis with your trained models
        result = handwriting_analyzer.analyze(filepath)
        
        # Add confirmation that real models were used
        result["real_models_used"] = True
        result["note"] = "Analysis completed using your trained CNN models"

        # Clean up temp file
        os.remove(filepath)

        return jsonify(result)

    except Exception as e:
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        print(f"❌ Error during REAL analysis: {e}")
        
        # Return error instead of fallback
        return jsonify({
            "error": f"Real model analysis failed: {str(e)}",
            "note": "Your trained models exist but analysis failed"
        }), 500

# Try to load analyzer after Flask app is created
def load_analyzer():
    global handwriting_analyzer, analyzer_error
    
    print("🚀 ATTEMPTING TO LOAD YOUR TRAINED CNN MODELS...")
    print(f"Models path: {MODELS_PATH}")
    print(f"Models directory exists: {os.path.exists(MODELS_PATH)}")
    
    if not os.path.exists(MODELS_PATH):
        analyzer_error = f"Models directory not found: {MODELS_PATH}"
        print(f"❌ {analyzer_error}")
        return
    
    try:
        files = os.listdir(MODELS_PATH)
        print(f"📁 Files in models directory: {files}")
        
        # Check for required files
        required_files = [
            'Copy of best_dheight_model.keras',
            'Copy of best_dloop_model.keras', 
            'Copy of best_gloop_model.keras',
            'Copy of best_t_mirrored_model.keras',
            'Copy of best_tloop_model.keras',
            'Copy of best_ttall_model.keras',
            'Copy of best_yloop_model.keras',
            'Copy of pressure_model.json',
            'Copy of spacing_model.json'
        ]
        
        missing_files = [f for f in required_files if f not in files]
        if missing_files:
            analyzer_error = f"Missing model files: {missing_files}"
            print(f"❌ {analyzer_error}")
            return
            
        print("✅ All required model files found!")
        
    except Exception as e:
        analyzer_error = f"Error listing model files: {str(e)}"
        print(f"❌ {analyzer_error}")
        return
    
    try:
        print("📦 Importing HandwritingAnalyzer...")
        from analyzer import HandwritingAnalyzer
        print("✅ HandwritingAnalyzer imported successfully")
        
        print("🧠 Loading your trained CNN models...")
        handwriting_analyzer = HandwritingAnalyzer(MODELS_PATH)
        print("🎉 SUCCESS! Your trained CNN models are loaded and ready!")
        
    except ImportError as e:
        analyzer_error = f"Import error - analyzer.py issue: {str(e)}"
        print(f"❌ Import failed: {analyzer_error}")
        handwriting_analyzer = None
        
    except Exception as e:
        analyzer_error = f"Model loading failed: {str(e)}"
        print(f"❌ Model loading error: {analyzer_error}")
        print(f"❌ Full error details: {repr(e)}")
        handwriting_analyzer = None

if __name__ == '__main__':
    # Start Flask app immediately
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask app on port {port}")
    
    # Load analyzer in background after app starts
    import threading
    analyzer_thread = threading.Thread(target=load_analyzer)
    analyzer_thread.daemon = True
    analyzer_thread.start()
    
    app.run(host='0.0.0.0', port=port, debug=False)
