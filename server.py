from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from app.planner import make_plan
import requests, uuid

app = FastAPI(title="Solvent Video Agent")
PIXVERSE = "https://app-api.pixverse.ai"

INDEX = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Solvent Video Agent</title><style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui;background:#090b10;color:#f3f5f7}main{max-width:1100px;margin:auto;padding:40px 20px 80px}.brand{font-weight:800;letter-spacing:.04em}.dot{display:inline-block;width:13px;height:13px;border-radius:50%;background:#26e6ff;box-shadow:0 0 28px #26e6ff;margin-right:10px}.hero{padding:55px 0 25px}h1{font-size:clamp(44px,7vw,82px);line-height:.94;letter-spacing:-.06em;margin:0 0 18px}.muted{color:#9298a6;max-width:760px;font-size:18px}.panel{background:linear-gradient(180deg,#11151e,#0d1118);border:1px solid #242a36;border-radius:22px;padding:22px;margin-top:20px}textarea,input,select{width:100%;background:#090c12;color:white;border:1px solid #2a3240;border-radius:14px;padding:14px;font:inherit}textarea{min-height:130px}.row{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}button{background:#e9fbff;color:#071014;border:0;border-radius:14px;padding:14px 18px;font-weight:800;cursor:pointer}.secondary{background:#161d28;color:#dbe7eb;border:1px solid #2a3443}.scene{border-top:1px solid #252c38;padding:20px 0}.prompt{white-space:pre-wrap;color:#c8d0d8;background:#0a0d13;border-radius:12px;padding:13px;margin:10px 0}.pill{display:inline-block;padding:6px 9px;border:1px solid #2c3744;border-radius:999px;color:#97a8b7;font-size:12px;margin:3px}.status{margin-top:12px;color:#7deaf6}.video{width:100%;max-width:360px;border-radius:14px;margin-top:12px;background:#05070a}.tiny{font-size:12px;color:#7f8998;margin-top:8px}.ok{color:#79e6a4}.err{color:#ff8f8f}@media(max-width:700px){.row{grid-template-columns:1fr}}</style></head><body><main><div class="brand"><span class="dot"></span>SOLVENT VIDEO AGENT · v2</div><section class="hero"><h1>Plan it.<br>Generate it.</h1><p class="muted">Create a continuity-aware Reel storyboard, then render individual scenes through PixVerse without exposing your API key in GitHub.</p></section><div class="panel"><label>PixVerse API key</label><input id="apiKey" type="password" placeholder="Paste API key here"><div class="tiny">Used only for requests from this page. It is not stored by this app.</div></div><div class="panel"><label>What should we create?</label><textarea id="idea">Your UX might not be the problem. Show how deeper business problems become visible through the interface.</textarea><div class="row"><select id="duration"><option value="30">30 seconds</option><option value="45">45 seconds</option><option value="60">60 seconds</option></select><button onclick="generatePlan()">✦ Generate Video Plan</button></div><div id="status" class="status"></div></div><div id="result" class="panel" style="display:none"></div><script>let plan=null;async function generatePlan(){status.textContent='Building continuity map…';const body=new URLSearchParams({idea:idea.value,duration:duration.value});const r=await fetch('/plan',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body});plan=await r.json();let html=`<h2>${plan.title}</h2><p><b>${plan.hook}</b></p><p class="muted">${plan.narration}</p><div>${plan.continuity_rules.map(x=>`<span class="pill">${x}</span>`).join('')}</div>`;for(const s of plan.scenes){html+=`<div class="scene"><h3>Scene ${s.id} · ${s.purpose}</h3><small>${s.duration}s · ${s.camera}</small><div class="prompt" id="p${s.id}">${s.prompt}</div><div class="row"><button class="secondary" onclick="navigator.clipboard.writeText(document.getElementById('p${s.id}').innerText)">Copy prompt</button><button onclick="generateScene(${s.id})">Generate Scene</button></div><div id="sceneStatus${s.id}" class="status"></div><div id="video${s.id}"></div></div>`}html+=`<button onclick="downloadManifest()">Export Manifest</button>`;result.innerHTML=html;result.style.display='block';status.textContent='Plan ready.'}async function generateScene(id){const key=apiKey.value.trim();if(!key){alert('Add your PixVerse API key first.');return}const s=plan.scenes.find(x=>x.id===id),el=document.getElementById('sceneStatus'+id);el.textContent='Submitting scene to PixVerse…';const body=new URLSearchParams({api_key:key,prompt:s.prompt,duration:'5'});const r=await fetch('/generate',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body});const d=await r.json();if(!r.ok||!d.video_id){el.className='status err';el.textContent=d.error||'Generation request failed.';return}el.className='status';el.textContent='Rendering…';pollScene(id,d.video_id,key)}async function pollScene(id,videoId,key){const el=document.getElementById('sceneStatus'+id);for(let i=0;i<60;i++){await new Promise(r=>setTimeout(r,5000));const body=new URLSearchParams({api_key:key,video_id:String(videoId)});const r=await fetch('/result',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body});const d=await r.json();if(d.status===1&&d.url){el.className='status ok';el.textContent='Scene ready.';document.getElementById('video'+id).innerHTML=`<video class="video" controls playsinline src="${d.url}"></video><p><a href="${d.url}" target="_blank">Open generated clip</a></p>`;return}if(d.error){el.className='status err';el.textContent=d.error;return}el.textContent='Rendering… '+((i+1)*5)+'s'}el.className='status err';el.textContent='Still rendering. Try Generate Scene again or check PixVerse.'}function downloadManifest(){const b=new Blob([JSON.stringify(plan,null,2)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='solvent-video-manifest.json';a.click()}</script></main></body></html>'''

@app.get("/", response_class=HTMLResponse)
def home(): return INDEX

@app.post("/plan")
def plan(idea: str = Form(...), duration: int = Form(30)):
    return JSONResponse(make_plan(idea, duration))

@app.post("/generate")
def generate(api_key: str = Form(...), prompt: str = Form(...), duration: int = Form(5)):
    try:
        headers={"API-KEY":api_key,"Ai-trace-id":str(uuid.uuid4()),"Content-Type":"application/json"}
        payload={"aspect_ratio":"9:16","duration":duration,"model":"v6","motion_mode":"normal","prompt":prompt,"quality":"720p","seed":0}
        r=requests.post(f"{PIXVERSE}/openapi/v2/video/text/generate",headers=headers,json=payload,timeout=30)
        data=r.json()
        if r.status_code>=400 or data.get("ErrCode") not in (0,None):
            return JSONResponse({"error":data.get("ErrMsg") or f"PixVerse error {r.status_code}"},status_code=400)
        return {"video_id":data.get("Resp",{}).get("video_id")}
    except Exception as e:
        return JSONResponse({"error":str(e)},status_code=500)

@app.post("/result")
def result(api_key: str = Form(...), video_id: str = Form(...)):
    try:
        headers={"API-KEY":api_key,"Ai-trace-id":str(uuid.uuid4())}
        r=requests.get(f"{PIXVERSE}/openapi/v2/video/result/{video_id}",headers=headers,timeout=20)
        data=r.json()
        if r.status_code>=400 or data.get("ErrCode") not in (0,None):
            return JSONResponse({"error":data.get("ErrMsg") or f"PixVerse error {r.status_code}"},status_code=400)
        resp=data.get("Resp",{})
        return {"status":resp.get("status"),"url":resp.get("url")}
    except Exception as e:
        return JSONResponse({"error":str(e)},status_code=500)

@app.get("/health")
def health(): return {"ok":True,"service":"solvent-video-agent","version":"2"}
