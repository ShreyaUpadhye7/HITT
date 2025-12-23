import React, { useState, useRef, useEffect } from 'react';

const CameraCapture = ({ onImageCapture, onClose }) => {
    const [isStreaming, setIsStreaming] = useState(false);
    const [capturedImage, setCapturedImage] = useState(null);
    const [error, setError] = useState('');
    const [cameraMode, setCameraMode] = useState('environment'); // 'user' for front, 'environment' for back
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const streamRef = useRef(null);

    useEffect(() => {
        return () => {
            // Cleanup: stop camera when component unmounts
            stopCamera();
        };
    }, []);

    const startCamera = async () => {
        try {
            setError('');
            
            // Stop existing stream if any
            stopCamera();

            const constraints = {
                video: {
                    facingMode: cameraMode,
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                }
            };

            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            streamRef.current = stream;
            
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                videoRef.current.play();
                setIsStreaming(true);
            }
        } catch (err) {
            console.error('Error accessing camera:', err);
            setError('Unable to access camera. Please ensure camera permissions are granted and try again.');
        }
    };

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        setIsStreaming(false);
    };

    const capturePhoto = () => {
        if (!videoRef.current || !canvasRef.current) {
            setError('Camera not ready. Please try again.');
            return;
        }

        const video = videoRef.current;
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');

        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Draw the video frame to canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert canvas to blob
        canvas.toBlob((blob) => {
            if (blob) {
                const imageUrl = URL.createObjectURL(blob);
                setCapturedImage(imageUrl);
                stopCamera();
            } else {
                setError('Failed to capture image. Please try again.');
            }
        }, 'image/jpeg', 0.9);
    };

    const retakePhoto = () => {
        if (capturedImage) {
            URL.revokeObjectURL(capturedImage);
            setCapturedImage(null);
        }
        startCamera();
    };

    const usePhoto = () => {
        if (!capturedImage || !canvasRef.current) {
            setError('No image captured. Please take a photo first.');
            return;
        }

        // Convert canvas to file
        canvasRef.current.toBlob((blob) => {
            if (blob) {
                const file = new File([blob], `handwriting-${Date.now()}.jpg`, { type: 'image/jpeg' });
                onImageCapture(file);
                onClose();
            } else {
                setError('Failed to process image. Please try again.');
            }
        }, 'image/jpeg', 0.9);
    };

    const switchCamera = () => {
        setCameraMode(prev => prev === 'user' ? 'environment' : 'user');
        if (isStreaming) {
            startCamera();
        }
    };

    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            onImageCapture(file);
            onClose();
        } else {
            setError('Please select a valid image file.');
        }
    };

    return (
        <div className="camera-capture-modal">
            <div className="camera-overlay">
                <div className="camera-container">
                    <div className="camera-header">
                        <h3>Capture Handwriting Sample</h3>
                        <button onClick={onClose} className="close-button">✕</button>
                    </div>

                    {error && (
                        <div className="camera-error">
                            <p>{error}</p>
                        </div>
                    )}

                    <div className="camera-content">
                        {!capturedImage ? (
                            <div className="camera-view">
                                <video
                                    ref={videoRef}
                                    className="camera-video"
                                    autoPlay
                                    playsInline
                                    muted
                                />
                                <canvas
                                    ref={canvasRef}
                                    className="capture-canvas"
                                    style={{ display: 'none' }}
                                />
                                
                                <div className="camera-overlay-guide">
                                    <div className="guide-frame">
                                        <div className="guide-text">
                                            Position handwriting sample within this frame
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="captured-preview">
                                <img src={capturedImage} alt="Captured handwriting" className="preview-image" />
                            </div>
                        )}
                    </div>

                    <div className="camera-controls">
                        {!capturedImage ? (
                            <>
                                {!isStreaming ? (
                                    <button onClick={startCamera} className="nav-button camera-button">
                                        📷 Start Camera
                                    </button>
                                ) : (
                                    <>
                                        <button onClick={capturePhoto} className="nav-button capture-button">
                                            📸 Capture Photo
                                        </button>
                                        <button onClick={switchCamera} className="nav-button switch-button">
                                            🔄 Switch Camera
                                        </button>
                                        <button onClick={stopCamera} className="nav-button stop-button">
                                            ⏹️ Stop Camera
                                        </button>
                                    </>
                                )}
                            </>
                        ) : (
                            <div className="preview-controls">
                                <button onClick={retakePhoto} className="nav-button retake-button">
                                    🔄 Retake
                                </button>
                                <button onClick={usePhoto} className="nav-button use-button">
                                    ✅ Use This Photo
                                </button>
                            </div>
                        )}
                    </div>

                    <div className="alternative-upload">
                        <div className="upload-divider">
                            <span>OR</span>
                        </div>
                        <label className="file-upload-button">
                            📁 Choose from Gallery
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleFileUpload}
                                style={{ display: 'none' }}
                            />
                        </label>
                    </div>

                    <div className="camera-tips">
                        <h4>📝 Tips for Best Results:</h4>
                        <ul>
                            <li>Ensure good lighting</li>
                            <li>Keep the handwriting flat and straight</li>
                            <li>Fill the frame with the writing sample</li>
                            <li>Avoid shadows and glare</li>
                            <li>Use a plain background if possible</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CameraCapture;