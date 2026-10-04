
from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import io
import re
import joblib
import numpy as np
import pytesseract 

from PIL import Image
from pdf2image import convert_from_bytes


app = FastAPI(title="Hospital Disease Risk API")

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),"final_models")

DISEASE_NAMES = {
    "DIQ010": "Diabetes",
    "BPQ020": "High Blood Pressure",
    "MCQ010": "Asthma",
    "MCQ160A": "Arthritis",
    "MCQ160B": "Congestive Heart Failure",
    "MCQ160C": "Coronary Heart Disease",
    "MCQ160D": "Angina",
    "MCQ160E": "Heart Attack",
    "MCQ160F": "Stroke",
    "MCQ160G": "Emphysema",
    "MCQ160K": "Chronic Bronchitis",
    "MCQ160L": "Liver Condition",
    "MCQ160M": "Thyroid Problem",
    "MCQ160N": "Gout",
    "MCQ160O": "COPD",
    "MCQ220": "Malignant Tumor"
}


# Load trained models
models = {}

if not os.path.exists(MODEL_DIR):
    raise FileNotFoundError(f"Model folder not found: {MODEL_DIR}")

for file in os.listdir(MODEL_DIR):
    if file.endswith(".joblib"):
        path = os.path.join(MODEL_DIR, file)
        models[file.replace(".joblib", "")] = joblib.load(path)


def number(value):
    if value is None:
        return None

    if isinstance(value, (int, float, np.number)):
        return float(value)

    match = re.search(r"-?\d+(?:\.\d+)?", str(value))

    if match:
        return float(match.group())

    return None


def predict(patient_data):

    results = []
    skipped = {}

    for disease, info in models.items():

        features = info["features"]
        model = info["model"]
        threshold = float(info["threshold"])

        missing = [
            feature
            for feature in features
            if feature not in patient_data
            or patient_data[feature] is None
        ]

        if missing:
            skipped[disease] = missing
            continue

        values = [
            number(patient_data[feature])
            for feature in features
        ]

        if any(value is None for value in values):
            skipped[disease] = features
            continue

        probability = float(
            model.predict_proba([values])[0][1]
        )

        risk = round(probability * 100, 2)

        if risk >= 70:
            risk_level = "High"
        elif risk >= 30:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        results.append({
            "disease_code": disease,
            "disease": DISEASE_NAMES.get(disease, disease),
            "risk_percent": risk,
            "risk_level": risk_level,
            "predicted_class": int(
                probability >= threshold
            )
        })

    results.sort(
        key=lambda x: x["risk_percent"],
        reverse=True
    )

    return {
        "status": "success",

        "results": results,

        "written_result": [
            {
                "disease": item["disease"],
                "risk_percent": item["risk_percent"],
                "risk_level": item["risk_level"],
                "message": (
                    f"{item['disease']}: "
                    f"{item['risk_percent']}% "
                    f"({item['risk_level']})"
                )
            }
            for item in results
        ],

        "graph_data": [
            {
                "disease": item["disease"],
                "risk_percent": item["risk_percent"]
            }
            for item in results
        ]
    }


# Manual patient data
@app.post("/predict")
def manual_predict(patient_data: dict):
    return predict(patient_data)


# OCR from PDF or image
def get_ocr(file_bytes, content_type):

    if content_type == "application/pdf":

        pages = convert_from_bytes(
            file_bytes,
            dpi=200
        )

    else:

        pages = [
            Image.open(
                io.BytesIO(file_bytes)
            )
        ]

    text = "\n".join(
        pytesseract.image_to_string(page)
        for page in pages
    )

    return text


# OCR text -> NHANES feature mapping
def extract_features(text):

    text = text.lower()

    patterns = {

        "RIDAGEYR":
            r"age\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "BMXBMI":
            r"bmi\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "BMXHT":
            r"height\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "BMXWT":
            r"weight\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "BMXWAIST":
            r"waist(?:\s+circumference)?\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "BPXSY1":
            r"systolic(?:\s+blood\s+pressure)?\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "BPXDI1":
            r"diastolic(?:\s+blood\s+pressure)?\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXGLU":
            r"(?:blood\s+)?glucose\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXGH":
            r"(?:hba1c|hb\s*a1c|a1c)\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXTC":
            r"total\s+cholesterol\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBDHDD":
            r"hdl(?:\s+cholesterol)?\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBDLDL":
            r"ldl(?:\s+cholesterol)?\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXTR":
            r"triglycerides\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXSCR":
            r"creatinine\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXSATSI":
            r"\balt\b\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXSASSI":
            r"\bast\b\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXSAL":
            r"albumin\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXSAPSI":
            r"alkaline\s+phosphatase\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXSTB":
            r"bilirubin\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXSBU":
            r"\bbun\b\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXHGB":
            r"(?:hemoglobin|haemoglobin)\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXWBCSI":
            r"\bwbc\b\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXPLTSI":
            r"platelets?\s*[:\-]?\s*(\d+(?:\.\d+)?)",

        "LBXCRP":
            r"\bcrp\b\s*[:\-]?\s*(\d+(?:\.\d+)?)"
    }

    data = {}

    for feature, pattern in patterns.items():

        match = re.search(
            pattern,
            text
        )

        if match:
            data[feature] = number(
                match.group(1)
            )

    if "female" in text:
        data["RIAGENDR"] = 2

    elif "male" in text:
        data["RIAGENDR"] = 1

    return data


# PDF/Image -> OCR -> Mapping -> Prediction
@app.post("/predict-report")
async def report_predict(
    file: UploadFile = File(...)
):

    allowed_types = {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Upload PDF, JPG, PNG or WEBP."
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    # OCR
    ocr_text = get_ocr(
        file_bytes,
        file.content_type
    )

    if not ocr_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No readable text found."
        )

    # Mapping
    patient_data = extract_features(
        ocr_text
    )

    if not patient_data:
        raise HTTPException(
            status_code=400,
            detail="No supported patient features found."
        )

    # Prediction
    result = predict(patient_data)

    # Clean response for frontend/backend
    return {
        "status": "success",
        "filename": file.filename,
        **result
    }
