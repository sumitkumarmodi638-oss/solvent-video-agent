from __future__ import annotations
import uuid, requests
from urllib.parse import urlparse

PIXVERSE = "https://app-api.pixverse.ai"
FAL_QUEUE = "https://queue.fal.run"


def submit_pixverse(api_key: str, prompt: str, duration: int = 5) -> dict:
    headers={"API-KEY":api_key,"Ai-trace-id":str(uuid.uuid4()),"Content-Type":"application/json"}
    payload={"aspect_ratio":"9:16","duration":duration,"model":"v6","motion_mode":"normal","prompt":prompt,"quality":"720p","seed":0}
    r=requests.post(f"{PIXVERSE}/openapi/v2/video/text/generate",headers=headers,json=payload,timeout=30)
    data=r.json()
    if r.status_code>=400 or data.get("ErrCode") not in (0,None):
        raise RuntimeError(data.get("ErrMsg") or f"PixVerse error {r.status_code}")
    return {"provider":"pixverse","job_id":str(data.get("Resp",{}).get("video_id"))}


def poll_pixverse(api_key: str, job_id: str) -> dict:
    headers={"API-KEY":api_key,"Ai-trace-id":str(uuid.uuid4())}
    r=requests.get(f"{PIXVERSE}/openapi/v2/video/result/{job_id}",headers=headers,timeout=20)
    data=r.json()
    if r.status_code>=400 or data.get("ErrCode") not in (0,None):
        raise RuntimeError(data.get("ErrMsg") or f"PixVerse error {r.status_code}")
    resp=data.get("Resp",{})
    return {"done":resp.get("status")==1,"status":resp.get("status"),"url":resp.get("url")}


def submit_fal_wan(api_key: str, prompt: str, duration: int = 5) -> dict:
    headers={"Authorization":f"Key {api_key}","Content-Type":"application/json","X-Fal-Store-IO":"0"}
    payload={"prompt":prompt,"aspect_ratio":"9:16","resolution":"480p","duration":str(5 if duration<=5 else 10),"enable_prompt_expansion":True,"enable_safety_checker":True}
    r=requests.post(f"{FAL_QUEUE}/fal-ai/wan-25-preview/text-to-video",headers=headers,json=payload,timeout=30)
    data=r.json()
    if r.status_code>=400:
        raise RuntimeError(data.get("detail") or data.get("message") or f"fal error {r.status_code}")
    return {"provider":"fal_wan","job_id":data.get("request_id"),"status_url":data.get("status_url"),"response_url":data.get("response_url")}


def _safe_fal_url(url: str) -> bool:
    try:
        return urlparse(url).hostname in {"queue.fal.run","fal.run"}
    except Exception:
        return False


def poll_fal_wan(api_key: str, status_url: str, response_url: str) -> dict:
    if not _safe_fal_url(status_url) or not _safe_fal_url(response_url):
        raise RuntimeError("Invalid fal queue URL")
    headers={"Authorization":f"Key {api_key}"}
    s=requests.get(status_url,headers=headers,timeout=20)
    status=s.json()
    if s.status_code>=400:
        raise RuntimeError(status.get("detail") or f"fal status error {s.status_code}")
    state=status.get("status")
    if state!="COMPLETED":
        return {"done":False,"status":state}
    r=requests.get(response_url,headers=headers,timeout=20)
    data=r.json()
    if r.status_code>=400:
        raise RuntimeError(data.get("detail") or f"fal result error {r.status_code}")
    url=(data.get("video") or {}).get("url")
    return {"done":bool(url),"status":"COMPLETED","url":url}


def submit(provider: str, api_key: str, prompt: str, duration: int = 5) -> dict:
    if provider=="pixverse": return submit_pixverse(api_key,prompt,duration)
    if provider=="fal_wan": return submit_fal_wan(api_key,prompt,duration)
    raise RuntimeError("Unsupported provider")


def poll(provider: str, api_key: str, job_id: str = "", status_url: str = "", response_url: str = "") -> dict:
    if provider=="pixverse": return poll_pixverse(api_key,job_id)
    if provider=="fal_wan": return poll_fal_wan(api_key,status_url,response_url)
    raise RuntimeError("Unsupported provider")
