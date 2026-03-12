# HITT – Hidden Intent Tracing Tool

## Research Paper

This repository contains the implementation of the research work:

**Hidden Intent Tracing Tool (HITT) for Handwriting Analysis to Identify the Intent of Alcohol-Dependent People Undergoing Treatment**

Authors:  
P.G Sunitha Hiremath  
Shreya Vijaykumar Upadhye  
Sweekruti S Nayak  
Tejaswini Mullalli  
Ganesh Birajdar  
Vivek V Pais  
Manjunath Nadagouda  

KLE Technological University, Hubballi, Karnataka, India  

Presented at:  
**3rd International Conference on Computing and Machine Learning (CML 2026)**

---

# Overview

Alcohol rehabilitation programs often struggle to identify whether patients are truly recovering or secretly showing signs of relapse.

The **Hidden Intent Tracing Tool (HITT)** is a machine learning system that analyzes handwriting samples to detect behavioral patterns related to recovery or relapse.

The system extracts handwriting features such as:

- Letter formation
- Writing pressure
- Word spacing
- Stroke patterns

These features are analyzed using **Convolutional Neural Networks (CNNs)** and traditional image processing techniques to identify psychological indicators linked to relapse risk.

The system also validates predictions using the **Alcohol Relapse Risk Scale (ARRS)** questionnaire.

---

# Motivation

Traditional relapse prediction methods rely on:

- Counselor observations
- Patient self-reports
- Behavioral interviews

However, these methods often fail to capture **hidden psychological intentions**.

Handwriting provides a behavioral signal that reflects subconscious emotional and cognitive states, making it a useful indicator for relapse detection. :contentReference[oaicite:1]{index=1}

---

# Dataset

Handwriting samples were collected from individuals undergoing alcohol rehabilitation treatment.

Data sources include:

- SDM De-Addiction and Research Center, Ujire
- Hope Recovery Center, Belgaum
- Manoshanti Psychiatry Hospital

Dataset characteristics:

- 75 handwriting samples
- Each participant wrote **three paragraphs**
- Images scanned and processed for feature extraction

Each sample was analyzed for:

- Pen pressure
- Word spacing
- Letter structures

Participants also completed the **ARRS questionnaire** to measure relapse risk.

---

# System Architecture

The HITT system follows a multi-stage pipeline:

1. Handwriting Sample Upload  
2. OCR Character Detection  
3. Letter Extraction  
4. CNN-based Trait Classification  
5. Pressure and Spacing Analysis  
6. Ensemble Model Prediction  
7. Report Generation

The final output provides a prediction indicating whether the handwriting suggests **recovery patterns or relapse tendencies**.

---

# Key Features

The system analyzes specific handwriting traits including:

- Loop structures in letters such as **g, y, d, t**
- Height of the **t-bar**
- Word spacing patterns
- Stroke pressure intensity

These features are processed through **six specialized CNN models** to detect behavioral traits.

---

# Methodology

## 1 Image Preprocessing

Handwriting images undergo preprocessing:

- Convert image to grayscale
- Resize to fixed resolution
- Normalize pixel values
- Apply thresholding and edge detection

This prepares the image for feature extraction.

---

## 2 Character Extraction

OCR is used to detect and extract target characters:

```
g, y, d, t, e
```

Each letter is cropped and stored for analysis.

---

## 3 CNN-Based Trait Detection

CNN models analyze extracted characters to detect handwriting traits such as:

- Loop presence
- Stroke direction
- Stem height
- Character shape variations

Each model predicts behavioral indicators associated with relapse or recovery.

---

## 4 Pressure Analysis

Pen pressure is estimated using grayscale intensity values.

Pressure levels are categorized as:

- Heavy Pressure
- Medium Pressure
- Light Pressure

Pressure patterns provide insights into emotional state.

---

## 5 Word Spacing Analysis

Spacing between words is measured using bounding boxes.

Spacing classification:

- Even spacing → emotional stability
- Uneven spacing → potential relapse indicators

---

## 6 Ensemble Model Integration

Predictions from:

- CNN models
- Pressure analysis
- Spacing analysis

are combined into an **ensemble model** for final relapse prediction.

---

## 7 Report Generation

The system generates a structured **Excel report** containing:

- Character counts
- Detected handwriting traits
- Relapse or recovery prediction score

This report can be used by clinicians and researchers for behavioral analysis.

---

# Results

The system demonstrated promising predictive performance.

CNN model accuracy examples:

| Trait Model | Accuracy (%) |
|-------------|-------------|
| d-Loop | 94.55 |
| t-Loop | 89.95 |
| Mirrored t | 87.58 |
| y-Loop | 92.70 |
| g-Loop | 80.29 |
| e-shape | 74.00 |

The **ensemble model achieved 90.6% accuracy** for relapse prediction. :contentReference[oaicite:2]{index=2}

The system also showed **87% agreement with ARRS questionnaire results**, validating its clinical usefulness.

---

# Technology Stack

Backend:

- Python
- TensorFlow / Keras
- OpenCV
- OCR (Space API)

Frontend:

- React.js

Database:

- MongoDB

Data Processing:

- Pandas
- OpenPyXL

---

# Project Structure

```
HITT
│
├── handwriting-project
│   ├── models
│   ├── preprocessing
│   ├── analysis
│
├── frontend
│   ├── React interface
│
├── backend
│   ├── Flask API
│
├── database
│   ├── MongoDB integration
│
└── README.md
```

---

# Running the Project

Clone the repository:

```bash
git clone https://github.com/ShreyaUpadhye7/HITT.git
cd HITT
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run backend server:

```bash
python app.py
```

Start frontend:

```bash
npm start
```

---

# Future Work

Future improvements may include:

- Larger dataset with more relapse cases
- Mobile-based handwriting monitoring
- Real-time handwriting analysis
- Integration with clinical health systems
- Additional handwriting traits such as stroke speed and direction

---

# Author

**Shreya Vijaykumar Upadhye**

Computer Science Engineering  
KLE Technological University  

Research Interests:

- AI in Healthcare
- Computer Vision
- Behavioral Data Analysis
- Machine Learning

---

# Citation

If you use this work, please cite:

```
Hiremath, P.G.S., Upadhye, S.V., Nayak, S.S., Mullalli, T., Birajdar, G., Pais, V.V., Nadagouda, M.
Hidden Intent Tracing Tool (HITT) for Handwriting Analysis to Identify the Intent of Alcohol-Dependent People Undergoing Treatment.
CML 2026.
```
