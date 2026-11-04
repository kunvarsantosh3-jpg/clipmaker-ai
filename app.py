from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import uuid, shutil, subprocess, json, re
BASE=Path(__file__).parent
WORK=BASE/"work"; WORK.mkdir(exist_ok=True)
app=FastAPI(title="ClipMaker AI Starter")
@app.get("/",response_class=HTMLResponse)
def home(): return (BASE/"templates"/"index.html").read_text(encoding="utf-8")
@app.post("/api/jobs")
async def create_job(video:UploadFile=File(...),target_seconds:int=Form(45)):
    if target_seconds not in (30,45,60): raise HTTPException(400,"Choose 30, 45 or 60 seconds")
    if not video.filename.lower().endswith((".mp4",".mov",".mkv",".webm",".m4v")): raise HTTPException(400,"Unsupported video")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"): raise HTTPException(500,"Server requires FFmpeg")
    jid=uuid.uuid4().hex[:12]; folder=WORK/jid; folder.mkdir()
    src=folder/("source"+Path(video.filename).suffix.lower()); size=0
    with src.open("wb") as out:
        while True:
            chunk=await video.read(1024*1024)
            if not chunk: break
            size+=len(chunk)
            if size>1_500_000_000:
                shutil.rmtree(folder,ignore_errors=True); raise HTTPException(413,"Max upload 1.5GB")
            out.write(chunk)
    pr=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(src)],capture_output=True,text=True)
    try: duration=float(json.loads(pr.stdout)["format"]["duration"])
    except: raise HTTPException(400,"Could not read video")
    clips=[]
    # Baseline slicing only; hook ranking is intentionally not falsely represented as AI.
    for i in range(min(20,max(1,int(duration//target_seconds)))):
        start=i*target_seconds
        if start>=duration: break
        length=min(target_seconds,duration-start); name=f"clip_{i+1:02}.mp4"; dest=folder/name
        cmd=["ffmpeg","-y","-ss",str(start),"-i",str(src),"-t",str(length),"-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920","-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-b:a","128k","-movflags","+faststart",str(dest)]
        run=subprocess.run(cmd,capture_output=True)
        if run.returncode==0 and dest.exists(): clips.append({"name":name,"url":f"/api/jobs/{jid}/clips/{name}","start":start})
    return {"job_id":jid,"duration_seconds":duration,"clips":clips,"message":"Fixed-interval clips generated; AI hooks/captions are not included in this starter."}
@app.get("/api/jobs/{jid}/clips/{filename}")
def download(jid:str,filename:str):
    if not re.fullmatch(r"clip_\d{2}\.mp4",filename): raise HTTPException(400,"Invalid name")
    path=WORK/jid/filename
    if not path.is_file(): raise HTTPException(404,"Not found")
    return FileResponse(path,media_type="video/mp4",filename=filename)
