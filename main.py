from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import yt_dlp
import tempfile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"]
)

# Future cookie use if needed
# COOKIE = os.getenv("TIKTOK_COOKIE")
# def write_cookie(cookie_str: str, tmpdir: str) -> str:
#     path = f"{tmpdir}/cookies.txt"
#     with open(path, "w") as f:
#         f.write(cookie_str)
#         return path

class DownloadRequest(BaseModel):
    url: str

@app.post("/download")
async def download(req: DownloadRequest):
    tmpdir = tempfile.TemporaryDirectory()
    try:
        opts = {
            "outtmpl": f"{tmpdir.name}/%(id)s.%(ext)s"
        }
        try: 
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(req.url, download=True)
                filename = ydl.prepare_filename(info)
            
            def stream():
                try:
                    with open(filename, "rb") as f:
                        yield from f
                finally:
                    tmpdir.cleanup()
            
            return StreamingResponse(
                stream(),
                media_type="video/mp4",
                headers={"Content-Disposition": f"attachment; filename={info['id']}.mp4"}
            )
        except Exception as e:
            tmpdir.cleanup()
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))