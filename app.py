from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.get("/", response_class=HTMLResponse)
async def serve_homepage():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>TurboDLmp4 Frontend File Missing on Server!</h1>"

@app.post("/download")
async def get_video_formats(request: VideoRequest):
    if not request.url:
        raise HTTPException(status_code=400, detail="URL missing")
        
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            formats = info.get('formats', [])
            title = info.get('title', 'Video')
            
            available_formats = []
            
            # Agar format list na mile to direct single URL nikalna (Fast fallback)
            single_url = info.get('url')
            if single_url:
                available_formats.append({
                    'quality': info.get('format_note', 'HD'),
                    'size': 'Auto Detect',
                    'url': single_url
                })
            
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    quality = f.get('format_note', f.get('resolution', 'N/A'))
                    filesize_bytes = f.get('filesize') or f.get('filesize_approx')
                    filesize = f"{filesize_bytes / (1024 * 1024):.2f} MB" if filesize_bytes else "Standard"
                    
                    available_formats.append({
                        'quality': quality,
                        'size': filesize,
                        'url': f.get('url')
                    })
            
            if available_formats:
                # Duplicates remove karne ke liye unique list
                seen = set()
                unique_formats = []
                for fmt in available_formats:
                    if fmt['quality'] not in seen:
                        seen.add(fmt['quality'])
                        unique_formats.append(fmt)
                return {"success": True, "title": title, "formats": unique_formats}
                
            return {"success": False, "message": "No stable MP4 formats found."}
    except Exception as e:
        return {"success": False, "message": str(e)}
      
