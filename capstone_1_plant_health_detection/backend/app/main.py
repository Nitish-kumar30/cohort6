from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import MAX_UPLOAD_BYTES, ALLOWED_CONTENT_TYPES
from app.pipeline import analyze_plant_image, PipelineError

app = FastAPI(title="Plant Health Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(image: UploadFile = File(...)):
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{image.content_type}'. Use JPEG, PNG, or WebP.",
        )

    image_bytes = await image.read()
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="Image too large (max 8 MB).")
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file upload.")

    try:
        result = analyze_plant_image(image_bytes, image.content_type)
    except PipelineError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result
