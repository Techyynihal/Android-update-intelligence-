# DroidSense AI — Android Update Predictor
## Setup & Run Guide

### Requirements
- Python 3.9+ 
- pip

---

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Train the ML Model
```bash
python model.py
```
This generates `model.pkl` in the project root.

### Step 3: Run the App
```bash
python app.py
```

### Step 4: Open in Browser
```
http://localhost:5000
```

---

### Project Structure
```
android_predictor/
├── app.py              ← Flask backend (routes + prediction engine)
├── model.py            ← ML training script (Random Forest)
├── model.pkl           ← Trained model (generated after step 2)
├── requirements.txt    ← Python dependencies
├── data/
│   └── update_data.csv ← 100+ synthetic training samples
├── templates/
│   └── index.html      ← Main frontend (dark glassmorphism UI)
└── static/
    ├── style.css       ← All styles
    └── script.js       ← Frontend JS (fetch API + animations)
```

---

### Features
- 17 smartphone brands supported (Samsung, Google, Xiaomi, Vivo, OPPO, etc.)
- 200+ device models
- ML-powered ETA and confidence predictions
- Rule-based fallback if ML confidence < 60%
- Offline mock data fallback if server unreachable
- Dark glassmorphism UI with animated gauges, timelines, feature chips

---

### Supported Brands
Chinese: Xiaomi, Redmi, POCO, Realme, iQOO, Vivo, OPPO, OnePlus, Huawei, Honor
Global: Samsung, Google (Pixel), Nothing, Motorola
Regional: Tecno, Infinix, Sharp
