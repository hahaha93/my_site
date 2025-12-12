from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.services.downloader import get_info, download_video, clean_url
import os

app = FastAPI()

class DownloadRequest(BaseModel):
    url: str
    # Removed playlist flag

@app.post("/info")
async def get_video_info(req: DownloadRequest):
    try:
        cleaned_url = clean_url(req.url)
        info = get_info(cleaned_url)
        return {
            "title": info.get('title', 'Unknown Title'),
            "id": info.get('id', 'Unknown ID'),
            "webpage_url": info.get('webpage_url', cleaned_url)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def remove_file(path: str):
    try:
        os.remove(path)
    except Exception as e:
        print(f"Error deleting file {path}: {e}")

@app.post("/download")
async def download(req: DownloadRequest, background_tasks: BackgroundTasks):
    try:
        cleaned_url = clean_url(req.url)
        file_path, title = download_video(cleaned_url)
        
        # Determine filename for the user
        ext = os.path.splitext(file_path)[1]
        filename = f"{title}{ext}"
        
        # Use original filename without strict ASCII sanitization
        # FastAPI/Starlette's FileResponse handles UTF-8 filenames correctly in Content-Disposition
        
        # Schedule file deletion after response is sent
        background_tasks.add_task(remove_file, file_path)
        
        return FileResponse(
            path=file_path, 
            filename=filename,
            media_type='application/octet-stream'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
