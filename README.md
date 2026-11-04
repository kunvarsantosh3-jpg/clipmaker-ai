# ClipMaker AI starter
Mobile friendly FastAPI + FFmpeg proof of concept.

## Run
Install Python 3.11+ and FFmpeg, then:
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
Visit http://localhost:8000

Docker:
docker build -t clipmaker .
docker run --rm -p 8000:8000 clipmaker

## Status
Working base: upload source video, split into fixed 30/45/60s excerpts, vertical crop, MP4 download.
Not yet implemented: YouTube URL ingestion, automatic AI highlight/hook ranking, transcript/captions, job queue or persistent storage. This is not yet the requested complete AI clipper.
Process only videos you own or have permission to use and comply with platform terms. Do not bypass access controls.
