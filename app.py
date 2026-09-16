from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import uvicorn

app = FastAPI()

# Website aur server ko aapas me fast connect karne ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.post("/download")
async def get_video_formats(request: VideoRequest):
    video_url = request.url
    if not video_url:
        raise HTTPException(status_code=400, detail="Link paste karein!")
        
    ydl_opts = {
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'quiet': True,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])
            title = info.get('title', 'Video')
            
            available_formats = []
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    quality = f.get('format_note', f.get('resolution', 'N/A'))
                    filesize_bytes = f.get('filesize') or f.get('filesize_approx')
                    filesize = f"{filesize_bytes / (1024 * 1024):.2f} MB" if filesize_bytes else "Unknown"
                        
                    available_formats.append({
                        'quality': quality,
                        'size': filesize,
                        'url': f.get('url')
                    })
            
            if available_formats:
                return {"success": True, "title": title, "formats": available_formats}
                
            return {"success": False, "message": "Koi munasib MP4 format nahi mil saka."}
                
    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)
