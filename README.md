# Solvent Video Agent v1

A zero-cost-first AI video workflow controller for creating short-form cinematic videos.

## Hosted test
- Generate a cinematic Reel plan from one idea.
- Create continuity-aware prompts for connected scenes.
- Export a JSON manifest.
- Hosted mode is optimized for Vercel.

## Local mode
The local build also supports FFmpeg assembly of generated MP4 clips.

## Run locally
```bash
python -m venv .venv
pip install -r requirements.txt
python run.py
```
Open `http://127.0.0.1:8787`.

## Deploy
Import this repository into Vercel. Vercel will detect the Python app through `server.py` and `vercel.json`.
