from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from app.planner import make_plan
from app.providers import submit, poll

app = FastAPI(title="Solvent Video Agent")

INDEX='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Solvent Video Agent</title><style>:root{color-scheme:dark}*{