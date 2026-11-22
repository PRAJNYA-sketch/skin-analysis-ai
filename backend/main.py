
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Skin Care AI",
    description="AI-powered Skin Analysis and Face Shape Recommendation System",
    version="1.0.0"
)

# Frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def home():
    return {
        "message": "Welcome to Skin Care AI",
        "status": "Backend is running"
    }


# Camera image endpoint
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
            detail="Uploaded image is empty"
        )

    return {
        "filename": file.filename,
        "message": "Face image received successfully",
        "size": len(image_data)
    }


# PDF report endpoint
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    pdf_data = await file.read()

    if not pdf_data:
        raise HTTPException(
            status_code=400,
            detail="PDF file is empty"
        )

    if not pdf_data.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file"
        )

    return {
        "filename": file.filename,
        "message": "PDF received successfully",
        "size": len(pdf_data)
    }
