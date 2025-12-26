from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from pathlib import Path
from uuid import uuid4

from compress import compress_video

BASE_DIR = Path(__file__).parent  # app/
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Video Compression API")

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi"}
MAX_SIZE_MB = 2048


@app.post("/compress")
async def compress(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Unsupported file type")

    uid = uuid4().hex
    input_path = UPLOAD_DIR / f"{uid}{ext}"
    original_name = Path(file.filename).stem
    output_path = OUTPUT_DIR / f"{original_name}_compressed.mp4"


    # Stream upload to disk
    size = 0
    with open(input_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_SIZE_MB * 1024 * 1024:
                raise HTTPException(status_code=413, detail="File too large")
            f.write(chunk)

    await file.close()

    # Run compression in background
    background_tasks.add_task(
        compress_video,
        input_path,
        output_path
    )

    return {
        "message": "Compression started",
        "output_path": str(output_path),
        "job_id": uid,
    }
