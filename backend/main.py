
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from PIL import Image
from io import BytesIO
import base64
import mediapipe as mp
import numpy as np
import os
from backend.recommendations import get_hairstyle_recommendations

from backend.recommendations import get_hairstyle_recommendations

app = FastAPI(
    title="Skin Care AI",
    description="AI-powered Skin Analysis and Face Shape Recommendation System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "face_landmarker.task"
)

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

face_options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=RunningMode.IMAGE,
    num_faces=1
)


@app.get("/")
def home():
    return {
        "message": "Welcome to Skin Care AI",
        "status": "Backend is running"
    }


# Estimate face shape
def estimate_face_shape(landmarks):

    def distance(point1, point2):
        return np.linalg.norm(
            np.array([point1.x, point1.y]) -
            np.array([point2.x, point2.y])
        )

    face_width = distance(landmarks[234], landmarks[454])
    forehead_width = distance(landmarks[103], landmarks[332])
    cheekbone_width = distance(landmarks[123], landmarks[352])
    jaw_width = distance(landmarks[172], landmarks[397])
    face_height = distance(landmarks[10], landmarks[152])

    if min(
        face_width,
        forehead_width,
        cheekbone_width,
        jaw_width,
        face_height
    ) <= 0:
        return "Unable to estimate"

    height_width_ratio = face_height / face_width
    jaw_forehead_ratio = jaw_width / forehead_width
    cheek_forehead_ratio = cheekbone_width / forehead_width

    if height_width_ratio >= 1.55:
        return "Oval"

    elif height_width_ratio <= 1.25:
        if jaw_forehead_ratio >= 0.85:
            return "Square"
        return "Round"

    elif cheek_forehead_ratio > 1.05:
        return "Diamond"

    elif jaw_forehead_ratio < 0.75:
        return "Heart"

    return "Oval"


# Face scan API
@app.post("/scan-face")
async def scan_face(file: UploadFile = File(...)):

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are allowed"
        )

    image_data = await file.read()

    if not image_data:
        raise HTTPException(
            status_code=400,
            detail="Image is empty"
        )

    try:
        image = Image.open(BytesIO(image_data)).convert("RGB")
        image_array = np.array(image)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=image_array
        )

        with FaceLandmarker.create_from_options(face_options) as landmarker:
            result = landmarker.detect(mp_image)

        if not result.face_landmarks:
            return {
                "face_detected": False,
                "message": "No face detected"
            }

        landmarks = result.face_landmarks[0]

        face_shape = estimate_face_shape(landmarks)

        hairstyle_recommendations = get_hairstyle_recommendations(
            face_shape
        )

        return {
            "filename": file.filename,
            "face_detected": True,
            "message": "Face analysis completed",
            "landmark_count": len(landmarks),
            "face_shape": face_shape,
            "hairstyle_recommendations": hairstyle_recommendations,
            "measurements": {
                "face_width": round(
                    float(np.linalg.norm(
                        np.array([landmarks[234].x, landmarks[234].y]) -
                        np.array([landmarks[454].x, landmarks[454].y])
                    )), 3
                ),
                "face_height": round(
                    float(np.linalg.norm(
                        np.array([landmarks[10].x, landmarks[10].y]) -
                        np.array([landmarks[152].x, landmarks[152].y])
                    )), 3
                )
            }
        }

    except Exception as error:
        print("Face analysis error:", error)
        raise HTTPException(
            status_code=500,
            detail="Face analysis failed"
        )


# PDF text and image extraction
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    pdf_data = await file.read()

    if not pdf_data or not pdf_data.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid or empty PDF"
        )

    try:
        pdf_reader = PdfReader(BytesIO(pdf_data))

        extracted_text = ""
        extracted_images = []

        for page_number, page in enumerate(pdf_reader.pages, start=1):

            extracted_text += page.extract_text() or ""
            extracted_text += "\n"

            for image in page.images:
                extracted_images.append({
                    "filename": image.name,
                    "page": page_number,
                    "image_base64": base64.b64encode(
                        image.data
                    ).decode("utf-8")
                })

        return {
            "filename": file.filename,
            "message": "PDF processed successfully",
            "pages": len(pdf_reader.pages),
            "extracted_text": extracted_text,
            "image_count": len(extracted_images),
            "images": extracted_images
        }

    except Exception as error:
        print("PDF extraction error:", error)
        raise HTTPException(
            status_code=400,
            detail="Unable to process PDF"
        )
