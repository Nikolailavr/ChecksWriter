from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import os
import uuid
from typing import Optional
from pydantic import BaseModel

from core import settings

app = FastAPI()
UPLOAD_DIR = settings.uploader.DIR

# Конфигурация
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")


class UploadResponse(BaseModel):
    status: str
    file_url: Optional[str] = None
    error: Optional[str] = None


@app.post("/upload/")
async def upload_photo(file: UploadFile = File(...)) -> UploadResponse:
    try:
        # Генерируем уникальное имя файла
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Формируем публичный URL
        file_url = f"/static/{filename}"

        return UploadResponse(status="success", file_url=file_url)

    except Exception as e:
        return UploadResponse(status="error", error=str(e))


@app.get("/list/")
async def list_files():
    files = os.listdir(UPLOAD_DIR)
    return {"files": [{"name": f, "url": f"/static/{f}"} for f in files]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
