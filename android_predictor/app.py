"""
Android Update Predictor - Flask Backend
Serves predictions via REST API using ML model + rule-based fallback
"""

from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import os
import json
from datetime import datetime, timedelta
import calendar

app = Flask(__name__)

# ─── Brand & Model Database ───────────────────────────────────────────────────

BRANDS_DATA = {
    "Samsung": {
        "ui": "One UI",
        "models": [
            "Galaxy S24 Ultra", "Galaxy S24+", "Galaxy S24",
            "Galaxy S23 Ultra", "Galaxy S23+", "Galaxy S23", "Galaxy S23 FE",
            "Galaxy S22 Ultra", "Galaxy S22+", "Galaxy S22",
            "Galaxy S21 Ultra", "Galaxy S21+", "Galaxy S21", "Galaxy S21 FE",
            "Galaxy A55", "Galaxy A54", "Galaxy A53", "Galaxy A34", "Galaxy A33",
            "Galaxy A14", "Galaxy A04s",
            "Galaxy M54", "Galaxy M34", "Galaxy M14",
            "Galaxy F54", "Galaxy F34",
            "Galaxy Z Fold 6", "Galaxy Z Fold 5", "Galaxy Z Fold 4",
            "Galaxy Z Flip 6", "Galaxy Z Flip 5", "Galaxy Z Flip 4"
        ]
    },
    "Google": {
        "ui": "Stock Android",
        "models": [
            "Pixel 9 Pro XL", "Pixel 9 Pro", "Pixel 9",
            "Pixel 8 Pro", "Pixel 8", "Pixel 8a",
            "Pixel 7 Pro", "Pixel 7", "Pixel 7a",
            "Pixel 6 Pro", "Pixel 6", "Pixel 6a",
            "Pixel Fold", "Pixel Tablet"
        ]
    },
    "OnePlus": {
        "ui": "OxygenOS",
        "models": [
            "OnePlus 12R", "OnePlus 12", "OnePlus 11R", "OnePlus 11",
            "OnePlus 10 Pro", "OnePlus 10T", "OnePlus 10R",
            "OnePlus Nord 4", "OnePlus Nord CE 4", "OnePlus Nord CE 3 Lite",
            "OnePlus Nord 3", "OnePlus Nord CE 3", "OnePlus Nord 2T",
            "OnePlus Open", "OnePlus Ace 3 Pro"
        ]
    },
    "Xiaomi": {
        "ui": "HyperOS",
        "models": [
            "Xiaomi 14 Ultra", "Xiaomi 14 Pro", "Xiaomi 14",
            "Xiaomi 13 Ultra", "Xiaomi 13 Pro", "Xiaomi 13", "Xiaomi 13T Pro", "Xiaomi 13T",
            "Xiaomi 12 Pro", "Xiaomi 12", "Xiaomi 12T Pro", "Xiaomi 12T",
            "Xiaomi Mix Fold 4", "Xiaomi Mix Fold 3",
            "Xiaomi Pad 6 Pro", "Xiaomi Pad 6"
        ]
    },
    "Redmi": {
        "ui": "HyperOS",
        "models": [
            "Redmi Note 13 Pro+", "Redmi Note 13 Pro", "Redmi Note 13",
            "Redmi Note 12 Pro+", "Redmi Note 12 Pro", "Redmi Note 12",
            "Redmi Note 11 Pro+", "Redmi Note 11 Pro", "Redmi Note 11",
            "Redmi 13C 5G", "Redmi 13C", "Redmi 12 5G", "Redmi 12",
            "Redmi A3", "Redmi A2+", "Redmi A2",
            "Redmi K70 Pro", "Redmi K70", "Redmi K60 Pro", "Redmi K60"
        ]
    },
    "POCO": {
        "ui": "HyperOS",
        "models": [
            "POCO F6 Pro", "POCO F6", "POCO F5 Pro", "POCO F5",
            "POCO X6 Pro", "POCO X6", "POCO X5 Pro", "POCO X5",
            "POCO M6 Pro 5G", "POCO M6 Pro", "POCO M6",
            "POCO C75", "POCO C65", "POCO C55"
        ]
    },
    "Realme": {
        "ui": "Realme UI",
        "models": [
            "Realme GT 6T", "Realme GT 6", "Realme GT 5 Pro", "Realme GT 5",
            "Realme GT Neo 6", "Realme GT Neo 5 SE", "Realme GT Neo 5",
            "Realme 12 Pro+", "Realme 12 Pro", "Realme 12+", "Realme 12",
            "Realme 11 Pro+", "Realme 11 Pro", "Realme 11",
            "Realme Narzo 70 Pro", "Realme Narzo 70", "Realme Narzo 60 Pro",
            "Realme C75", "Realme C65", "Realme C55"
        ]
    },
    "iQOO": {
        "ui": "FuntouchOS",
        "models": [
            "iQOO 12 Pro", "iQOO 12", "iQOO 11 Pro", "iQOO 11",
            "iQOO Neo 9 Pro", "iQOO Neo 9", "iQOO Neo 8 Pro", "iQOO Neo 8",
            "iQOO Z9 Turbo", "iQOO Z9 Pro", "iQOO Z9", "iQOO Z7 Pro", "iQOO Z7",
            "iQOO 13"
        ]
    },
    "Vivo": {
        "ui": "FuntouchOS",
        "models": [
            "Vivo X100 Ultra", "Vivo X100 Pro", "Vivo X100",
            "Vivo X90 Pro+", "Vivo X90 Pro", "Vivo X90",
            "Vivo X Fold 3 Pro", "Vivo X Fold 3", "Vivo X Fold 2",
            "Vivo V40 Pro", "Vivo V40", "Vivo V30 Pro", "Vivo V30",
            "Vivo Y200 Pro", "Vivo Y200", "Vivo Y100A", "Vivo Y100",
            "Vivo T3 Pro", "Vivo T3x", "Vivo T3", "Vivo T2 Pro", "Vivo T2",
            "Vivo Y38 5G", "Vivo Y28 5G", "Vivo Y18s"
        ]
    },
    "OPPO": {
        "ui": "ColorOS",
        "models": [
            "OPPO Find X8 Ultra", "OPPO Find X8 Pro", "OPPO Find X8",
            "OPPO Find X7 Ultra", "OPPO Find X7",
            "OPPO Find N3 Flip", "OPPO Find N3",
            "OPPO Reno 12 Pro", "OPPO Reno 12", "OPPO Reno 11 Pro", "OPPO Reno 11",
            "OPPO Reno 10 Pro+", "OPPO Reno 10 Pro", "OPPO Reno 10",
            "OPPO A3 Pro", "OPPO A3", "OPPO A79", "OPPO A78"
        ]
    },
    "Huawei": {
        "ui": "HarmonyOS",
        "models": [
            "Huawei Mate 60 Pro+", "Huawei Mate 60 Pro", "Huawei Mate 60",
            "Huawei Mate X5", "Huawei Mate X3",
            "Huawei P60 Pro", "Huawei P60 Art", "Huawei P60",
            "Huawei Nova 12 Ultra", "Huawei Nova 12 Pro", "Huawei Nova 12",
            "Huawei Pura 70 Ultra", "Huawei Pura 70 Pro+", "Huawei Pura 70 Pro"
        ]
    },
    "Honor": {
        "ui": "MagicOS",
        "models": [
            "Honor Magic 6 Ultimate", "Honor Magic 6 Pro", "Honor Magic 6",
            "Honor Magic 5 Pro", "Honor Magic 5 Ultimate",
            "Honor Magic V2", "Honor Magic V3",
            "Honor 90 Pro", "Honor 90", "Honor 80 Pro", "Honor 80",
            "Honor X9b", "Honor X9a", "Honor X8b", "Honor X7b",
            "Honor 200 Pro", "Honor 200"
        ]
    },
    "Motorola": {
        "ui": "Hello UI",
        "models": [
            "Motorola Edge 50 Ultra", "Motorola Edge 50 Pro", "Motorola Edge 50",
            "Motorola Edge 40 Pro", "Motorola Edge 40 Neo", "Motorola Edge 40",
            "Motorola Edge 30 Ultra", "Motorola Edge 30 Pro",
            "Moto G85", "Moto G84", "Moto G54 5G", "Moto G54", "Moto G34",
            "Moto G Power 2024", "Moto G Stylus 2024",
            "Motorola Razr 50 Ultra", "Motorola Razr 50", "Motorola Razr 40 Ultra"
        ]
    },
    "Nothing": {
        "ui": "Nothing OS",
        "models": [
            "Nothing Phone 2a Plus", "Nothing Phone 2a", "Nothing Phone 2", "Nothing Phone 1",
            "Nothing CMF Phone 1"
        ]
    },
    "Tecno": {
        "ui": "HiOS",
        "models": [
            "Tecno Phantom V Fold 2", "Tecno Phantom V Fold", "Tecno Phantom V Flip",
            "Tecno Pova 6 Pro", "Tecno Pova 6", "Tecno Pova 5 Pro",
            "Tecno Camon 30 Premier", "Tecno Camon 30 Pro 5G", "Tecno Camon 30",
            "Tecno Spark 20 Pro+", "Tecno Spark 20 Pro", "Tecno Spark 20"
        ]
    },
    "Infinix": {
        "ui": "XOS",
        "models": [
            "Infinix Zero 40", "Infinix Zero 30 5G", "Infinix Zero 30",
            "Infinix Note 40 Pro+", "Infinix Note 40 Pro", "Infinix Note 40",
            "Infinix Hot 40 Pro", "Infinix Hot 40", "Infinix Hot 30 Play",
            "Infinix Smart 8 Plus", "Infinix Smart 8 Pro", "Infinix Smart 8"
        ]
    },
    "Sharp": {
        "ui": "Stock-based UI",
        "models": [
            "Sharp Aquos R9 Pro", "Sharp Aquos R9", "Sharp Aquos R8s Pro", "Sharp Aquos R8s",
            "Sharp Aquos R8 Pro", "Sharp Aquos R8",
            "Sharp Aquos Sense 9", "Sharp Aquos Sense 8", "Sharp Aquos Wish 4"
        ]
    }
}

# ─── Update History ────────────────────────────────────────────────────────────

UPDATE_HISTORY = {
    "Samsung": ["One UI 4.0 (Android 12)", "One UI 5.0 (Android 13)", "One UI 6.0 (Android 14)"],
    "Google": ["Android 12", "Android 13", "Android 14"],
    "OnePlus": ["OxygenOS 12 (Android 12)", "OxygenOS 13 (Android 13)", "OxygenOS 14 (Android 14)"],
    "Xiaomi": ["MIUI 13 (Android 12)", "HyperOS 1.0 (Android 13)", "HyperOS 2.0 (Android 14)"],
    "Redmi": ["MIUI 13 (Android 12)", "HyperOS 1.0 (Android 13)", "HyperOS 2.0 (Android 14)"],
    "POCO": ["MIUI 13 (Android 12)", "HyperOS 1.0 (Android 13)", "HyperOS 2.0 (Android 14)"],
    "Realme": ["Realme UI 3.0 (Android 12)", "Realme UI 4.0 (Android 13)", "Realme UI 5.0 (Android 14)"],
    "iQOO": ["FuntouchOS 12", "FuntouchOS 13", "FuntouchOS 14"],
    "Vivo": ["FuntouchOS 12 (Android 12)", "FuntouchOS 13 (Android 13)", "FuntouchOS 14 (Android 14)"],
    "OPPO": ["ColorOS 12 (Android 12)", "ColorOS 13 (Android 13)", "ColorOS 14 (Android 14)"],
    "Huawei": ["HarmonyOS 3.0", "HarmonyOS 3.1", "HarmonyOS 4.0"],
    "Honor": ["MagicOS 7.0 (Android 13)", "MagicOS 7.1", "MagicOS 8.0 (Android 14)"],
    "Motorola": ["Android 12", "Android 13", "Android 14"],
    "Nothing": ["Nothing OS 1.5 (Android 12)", "Nothing OS 2.0 (Android 13)", "Nothing OS 2.5 (Android 14)"],
    "Tecno": ["HiOS 12 (Android 12)", "HiOS 13 (Android 13)", "HiOS 14 (Android 14)"],
    "Infinix": ["XOS 12 (Android 12)", "XOS 13 (Android 13)", "XOS 14 (Android 14)"],
    "Sharp": ["Android 12", "Android 13", "Android 14"]
}

# ─── Features per Android version ─────────────────────────────────────────────

ANDROID_FEATURES = {
    "14": [
        "Predictive Back Gesture", "Health Connect integration",
        "Per-app language settings", "Photo picker privacy controls",
        "Improved satellite connectivity"
    ],
    "15": [
        "Android AI Core on-device AI", "Adaptive Refresh Rate improvements",
        "Partial screen sharing", "Satellite messaging support",
        "Advanced thermal management", "Dynamic island-style alerts",
        "Improved privacy sandbox", "App archiving enhancements"
    ],
    "16": [
        "Full AI OS integration", "Cross-device continuity",
        "Advanced gesture navigation 3.0", "Holographic display support",
        "Neural processing layer", "Adaptive UI morphing",
        "Quantum-safe encryption", "Seamless cloud-local switching"
    ]
}

UI_FEATURES = {
    "Samsung": {
        "7": ["Galaxy AI features", "Now Bar live activities", "Cross-app actions", "AI Live Translate improvements", "Sketch to Image AI"],
        "8": ["Advanced AI agents", "Adaptive wallpapers", "Smart home hub 2.0", "AI power management"]
    },
    "Google": {
        "15": ["Gemini Nano deep integration", "Circle to Search improvements", "Live transcription", "AI-powered photo unblur"],
        "16": ["Gemini Ultra on-device", "Project Astra integration", "AI Assistant redesign", "Pixel Screenshots AI"]
    },
    "OnePlus": {
        "14": ["Trinity Engine 2.0", "Smart Vibration 2.0", "O-Haptics improvements", "Canvas AOD upgrade"],
        "15": ["AI-powered OnePlus Intelligence", "Spatial audio", "Adaptive Display 3.0", "Zen Mode AI"]
    },
    "default": {
        "next": ["AI assistant integration", "Privacy dashboard upgrade", "Improved RAM management", "Smoother animations", "Enhanced camera algorithms"]
    }
}

# ─── Load ML Model ─────────────────────────────────────────────────────────────

MODEL = None

def load_model():
    global MODEL
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    if os.path.exists(model_path):
        MODEL = joblib.load(model_path)
        print("[✓] ML model loaded")
    else:
        print("[!] model.pkl not found — training now...")
        from model import train_model
        MODEL = train_model()

# ─── Prediction Engine ─────────────────────────────────────────────────────────

def get_next_android(current_ver_str):
    try:
        ver = float(str(current_ver_str).replace("Android ", "").strip())
        if ver < 14:
            return f"Android 14", 14
        elif ver == 14:
            return "Android 15", 15
        elif ver == 15:
            return "Android 16", 16
        else:
            return f"Android {int(ver)+1}", int(ver)+1
    except:
        return "Android 15", 15

def get_next_ui(brand, current_ui_str):
    brand_info = BRANDS_DATA.get(brand, {})
    ui_name = brand_info.get("ui", "Stock Android")

    ui_map = {
        "One UI": {"6": "7.0", "6.1": "7.0", "7": "7.5", "default": "7.0"},
        "Stock Android": {"14": "15", "15": "16", "default": "15"},
        "OxygenOS": {"13": "14.0", "14": "15.0", "default": "14.0"},
        "HyperOS": {"1": "2.0", "2": "3.0", "default": "2.0"},
        "Realme UI": {"4": "5.0", "5": "6.0", "default": "5.0"},
        "FuntouchOS": {"13": "14.0", "14": "15.0", "default": "14.0"},
        "ColorOS": {"13": "14.0", "14": "15.0", "default": "14.0"},
        "HarmonyOS": {"4": "4.2", "4.2": "5.0", "default": "4.2"},
        "MagicOS": {"7": "8.0", "8": "9.0", "default": "8.0"},
        "Hello UI": {"stock": "Android 15", "default": "Android 15"},
        "Nothing OS": {"2": "3.0", "2.5": "3.0", "default": "3.0"},
        "HiOS": {"13": "14.0", "14": "15.0", "default": "14.0"},
        "XOS": {"13": "14.0", "14": "15.0", "default": "14.0"},
        "Stock-based UI": {"default": "Android 15"},
    }

    brand_map = ui_map.get(ui_name, {"default": "Next Version"})

    for key in brand_map:
        if key != "default" and key in str(current_ui_str):
            return f"{ui_name} {brand_map[key]}"

    return f"{ui_name} {brand_map.get('default', 'Next')}"

def get_security_patch_eta():
    now = datetime.now()
    next_month = now + timedelta(days=30)
    month_name = calendar.month_name[next_month.month]
    return f"Monthly — Next patch: {month_name} {next_month.year}"

def get_likelihood(confidence):
    if confidence >= 80:
        return "High"
    elif confidence >= 65:
        return "Medium"
    else:
        return "Low"

def get_features(brand, next_android_ver, next_ui_ver):
    android_ver_key = str(next_android_ver)
    android_feats = ANDROID_FEATURES.get(android_ver_key, ANDROID_FEATURES["15"])

    brand_ui_feats = UI_FEATURES.get(brand, UI_FEATURES["default"])
    ui_key = str(next_ui_ver).split(".")[0] if "." in str(next_ui_ver) else str(next_ui_ver)
    ui_feats = brand_ui_feats.get(ui_key, brand_ui_feats.get("next", UI_FEATURES["default"]["next"]))

    combined = ui_feats[:3] + android_feats[:3]
    return combined[:6]

def predict_with_ml(brand, model_name, android_ver, ui_ver):
    """Use ML model for prediction"""
    try:
        le_brand = MODEL['le_brand']
        le_model = MODEL['le_model']
        eta_model = MODEL['eta_model']
        conf_model = MODEL['conf_model']

        if brand not in le_brand.classes_:
            return None

        brand_enc = le_brand.transform([brand])[0]
        model_enc = 0
        if model_name in le_model.classes_:
            model_enc = le_model.transform([model_name])[0]

        try:
            ver_float = float(str(android_ver).replace("Android", "").strip())
        except:
            ver_float = 14.0

        launch_year = 2023
        update_months = 6
        patch_freq = 6

        X = np.array([[brand_enc, model_enc, launch_year, ver_float, update_months, patch_freq]])

        eta = float(eta_model.predict(X)[0])
        conf = float(conf_model.predict(X)[0])
        conf = max(50, min(98, conf))
        eta = max(1, min(18, round(eta)))

        return {"eta_months": eta, "confidence": conf}
    except Exception as e:
        print(f"[ML Error]: {e}")
        return None

def rule_based_predict(brand, model_name, android_ver, ui_ver):
    """Rule-based fallback prediction"""
    try:
        ver = float(str(android_ver).replace("Android", "").strip())
    except:
        ver = 14.0

    premium_brands = {"Google": 95, "Samsung": 88, "OnePlus": 82, "Nothing": 83}
    mid_brands = {"Xiaomi": 80, "Redmi": 76, "POCO": 77, "Realme": 74, "iQOO": 78, "Vivo": 75, "OPPO": 76, "Honor": 74, "Motorola": 75}
    base_brands = {"Huawei": 60, "Tecno": 65, "Infinix": 63, "Sharp": 68}

    base_conf = premium_brands.get(brand, mid_brands.get(brand, base_brands.get(brand, 68)))

    # Newer android = slightly higher confidence
    if ver >= 14:
        base_conf = min(98, base_conf + 5)
    elif ver < 12:
        base_conf = max(50, base_conf - 10)

    # ETA estimation
    eta_map = {
        "Google": 1, "Samsung": 2, "Nothing": 2, "OnePlus": 3,
        "Xiaomi": 3, "Realme": 4, "iQOO": 3, "Vivo": 4,
        "OPPO": 4, "POCO": 4, "Redmi": 5, "Honor": 4,
        "Motorola": 4, "Huawei": 8, "Tecno": 7, "Infinix": 7, "Sharp": 6
    }
    eta = eta_map.get(brand, 5)

    return {"eta_months": eta, "confidence": base_conf}

def format_eta(eta_months):
    now = datetime.now()
    future = now + timedelta(days=eta_months * 30)
    quarter = f"Q{(future.month - 1) // 3 + 1}"
    year = future.year
    if eta_months <= 1:
        return f"~{eta_months} month ({quarter} {year})"
    return f"{eta_months}–{eta_months + 1} months ({quarter} {year})"

# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({"status": "ok", "model_loaded": MODEL is not None, "version": "2.0.0"})

@app.route('/brands')
def get_brands():
    result = {}
    for brand, info in BRANDS_DATA.items():
        result[brand] = {
            "ui": info["ui"],
            "models": info["models"],
            "history": UPDATE_HISTORY.get(brand, [])
        }
    return jsonify(result)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    brand = data.get('brand', '').strip()
    model_name = data.get('model', '').strip()
    android_ver = data.get('android_version', '14')
    ui_ver = data.get('ui_version', '')

    if not brand or not model_name:
        return jsonify({"error": "Brand and model are required"}), 400

    # Try ML model first
    ml_result = None
    if MODEL:
        ml_result = predict_with_ml(brand, model_name, android_ver, ui_ver)

    # Use ML or fallback
    if ml_result and ml_result['confidence'] >= 60:
        pred = ml_result
    else:
        pred = rule_based_predict(brand, model_name, android_ver, ui_ver)

    eta_months = pred['eta_months']
    confidence = round(pred['confidence'])

    # Build predictions
    next_android, next_android_num = get_next_android(android_ver)
    next_ui = get_next_ui(brand, ui_ver)
    features = get_features(brand, next_android_num, ui_ver)
    security_patch = get_security_patch_eta()
    eta_str = format_eta(eta_months)
    likelihood = get_likelihood(confidence)
    history = UPDATE_HISTORY.get(brand, ["Android 12", "Android 13", "Android 14"])

    response = {
        "next_android": next_android,
        "next_ui": next_ui,
        "features": features,
        "security_patch": security_patch,
        "eta": eta_str,
        "confidence": confidence,
        "likelihood": likelihood,
        "history": history,
        "brand": brand,
        "model": model_name
    }

    return jsonify(response)

# ─── App Entry ─────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    load_model()
    app.run(debug=True, host='0.0.0.0', port=5000)
