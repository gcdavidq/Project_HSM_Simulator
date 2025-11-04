from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import hashlib
from datetime import datetime

# -------------------------------------------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# -------------------------------------------------------------
app = FastAPI(
    title="🔐 HSM Master Key Simulator API",
    description=(
        "API para registrar custodios y enviar shares de claves maestras. "
        "Cada share se valida, se genera su hash automáticamente y se almacena "
        "con un sello de tiempo para trazabilidad."
    ),
    version="1.5.1",
    contact={
        "name": "Equipo de Desarrollo",
        "email": "soporte@hsm-simulator.local",
    },
)

# -------------------------------------------------------------
# MODELOS DE DATOS
# -------------------------------------------------------------
class Custodian(BaseModel):
    custodian_id: str
    password: str


class Share(BaseModel):
    custodian_id: str
    password: str
    share_data: str


# -------------------------------------------------------------
# ALMACENAMIENTO TEMPORAL
# -------------------------------------------------------------
custodians = {}
shares = []

@app.get("/", response_class=HTMLResponse, tags=["Inicio"])
def root():
    html_content = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>HSM Master Key Simulator</title>
<style>
  :root{
    --bg-1: #0b0c0f;
    --bg-2: #101214;
    --accent-green: #7CFF3B;
    --muted: #98a0ad;
  }
  *{box-sizing:border-box;}
  html,body{height:100%; margin:0; font-family: -apple-system, "SF Pro Text", "Segoe UI", Roboto, Arial, sans-serif; -webkit-font-smoothing:antialiased;}
  body{
    background: radial-gradient(1200px 800px at 10% 10%, rgba(40,44,52,0.4), rgba(6,8,10,0.9)),
                linear-gradient(180deg,var(--bg-1),var(--bg-2));
    color:#fff;
    overflow:hidden;
  }

  .grid {
    position:fixed; inset:0; pointer-events:none; z-index:0;
    background-image:
      linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 60px 60px, 60px 60px;
    opacity:0.12;
  }

  .stage {
    position:relative;
    z-index:2;
    min-height:100vh;
    display:flex;
    align-items:center;
    justify-content:center;
    padding:48px;
  }

  .hero {
    width:100%;
    max-width:1180px;
    display:grid;
    grid-template-columns: 1fr 420px;
    gap:36px;
    align-items:center;
    position:relative;
  }

  .left {
    padding:28px 18px;
  }
  .headline{
    font-size:48px;
    line-height:1.02;
    margin:0 0 14px 0;
    font-weight:800;
    display:flex;
    flex-wrap:wrap;
    gap:8px;
  }
  .headline .muted { color:var(--muted); font-weight:600 }

  .sub {
    color:var(--muted);
    font-size:16px;
    max-width:680px;
    margin-bottom:26px;
  }

  .ctas { display:flex; gap:16px; align-items:center; }
  .btn {
    padding:14px 28px; border-radius:999px; font-weight:800; cursor:pointer; border:none; color:#081018;
  }
  .btn-primary {
    background: linear-gradient(90deg, #9CFF5A, #6EE07C);
    box-shadow: 0 18px 50px rgba(120,255,100,0.12);
  }
  .btn-secondary {
    background: transparent; border:1px solid rgba(255,255,255,0.06); color:var(--muted); padding:12px 20px; border-radius:14px; font-weight:700;
  }

  .card {
    background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
    border-radius:20px;
    padding:22px;
    box-shadow: 0 20px 60px rgba(2,6,23,0.3);
    border:1px solid rgba(255,255,255,0.06);
    min-height:420px;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
}

.grid {
    position:fixed; inset:0; pointer-events:none; z-index:0;
    background-image:
      linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 60px 60px, 60px 60px;
    opacity:0.12;
}

.stage {
    position:relative;
    z-index:2;
    min-height:100vh;
    display:flex;
    align-items:center;
    justify-content:center;
    padding:48px;
}

.hero {
    width:100%;
    max-width:1180px;
    display:grid;
    grid-template-columns: 1fr 420px;
    gap:36px;
    align-items:center;
}

.left { padding:28px 18px; }

.headline {
    font-size:48px;
    line-height:1.02;
    margin:0 0 14px 0;
    font-weight:800;
    display:flex;
    flex-wrap:wrap;
    gap:8px;
}

.headline .muted { color:var(--muted); font-weight:600; }

.sub {
    color:var(--muted);
    font-size:16px;
    max-width:680px;
    margin-bottom:26px;
}

.ctas { display:flex; gap:16px; align-items:center; }

.btn {
    padding:14px 28px;
    border-radius:999px;
    font-weight:800;
    cursor:pointer;
    border:none;
    color:#081018;
}

.btn-primary {
    background: linear-gradient(90deg, #9CFF5A, #6EE07C);
    box-shadow: 0 18px 50px rgba(120,255,100,0.12);
}

.btn-secondary {
    background: transparent;
    border:1px solid rgba(255,255,255,0.06);
    color:var(--muted);
    padding:12px 20px;
    border-radius:14px;
    font-weight:700;
}

.terminal-mini {
    background: linear-gradient(180deg, rgba(0,0,0,0.35), rgba(0,0,0,0.2));
    color: #B7FFE0;
    padding:12px;
    border-radius:12px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", monospace;
    font-size:13px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
}

@media (max-width:980px){
    .hero{ grid-template-columns: 1fr; padding:24px 8px; }
    .card{ min-height:260px; order:2; }
    .headline{ font-size:32px; }
}
</style>
</head>
<body>
  <div class="grid" aria-hidden="true"></div>
  <div class="stage">
    <div class="hero">

      <div class="left">
        <div class="headline" aria-hidden="false">
          <span class="muted">HSM Master Key Simulator</span>
          <span class="reveal-wrap" style="margin-left:6px;">
            <span id="brand-name" class="typewriter">Critografia_y_seguridad</span>
            <span class="reveal-mask" id="reveal-mask"></span>
          </span>
        </div>

        <div class="sub">Este es un simulador de HSM que permite manejar fragmentos de claves de forma segura, registrar custodios, validar cada fragmento automáticamente y tener un registro auditado, todo con una interfaz web profesional y moderna.</div>

        <div class="ctas">
          <button class="btn btn-primary" onclick="location.href='/docs'">Get Started</button>
        </div>
      </div>

      <div class="card" aria-hidden="false">
        <div>
          <div style="display:flex;align-items:center;gap:12px">
            <div style="width:48px;height:48px;border-radius:10px;background:linear-gradient(180deg,#e6f8ff,#ffffff);display:grid;place-items:center">
              <img src="https://cdn-icons-png.flaticon.com/512/4149/4149670.png" alt="logo small" style="width:22px">
            </div>
            <div>
              <div style="font-weight:800;font-size:16px;color:#fff">HSM Master</div>
              <div style="font-size:13px;color:var(--muted)">FastAPI · Demo local</div>
            </div>
          </div>

          <div class="lock-wrap" style="position:relative; margin-top:18px;">
            <div class="lines" aria-hidden="true">
              <svg width="100%" height="220" viewBox="0 0 600 220" preserveAspectRatio="none" style="position:absolute;left:0;top:0;opacity:0.28">
                <defs>
                  <linearGradient id="g1" x1="0" x2="1">
                    <stop offset="0" stop-color="#7cff3b" stop-opacity="0.9"/>
                    <stop offset="1" stop-color="#00d4ff" stop-opacity="0.7"/>
                  </linearGradient>
                </defs>
                <polyline points="10,160 120,120 220,140 320,110 420,140 520,115" fill="none" stroke="url(#g1)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                <circle cx="120" cy="120" r="6" fill="#7cff3b"/>
                <circle cx="320" cy="110" r="6" fill="#00d4ff"/>
              </svg>
            </div>

            <div class="lock" role="img" aria-label="padlock">
              <div class="shackle" style="border-color: rgba(200,200,200,0.8);"></div>
              <div class="body"> 
                <div style="text-align:center;color:var(--muted);font-weight:700">HSM</div>
              </div>
              <div class="leds" aria-hidden><span style="background:#7cff3b"></span><span style="background:#7cff3b"></span><span style="background:#7cff3b"></span></div>
            </div>
          </div>

        </div>

        <div style="display:flex;flex-direction:column;gap:12px">
          <div class="terminal-mini" id="mini-term">
            &gt; Estado del sistema: <strong style="color:#fff">OK</strong><br>
            &gt; Última sincronización  : <span id="last-sync">—</span>
          </div>

          <div style="display:flex;gap:12px; justify-content:space-between; align-items:center;">
            <div style="color:var(--muted); font-size:13px">Custodios registrados</div>
            <div id="cust-count" style="font-weight:800; color:#fff">0</div>
          </div>
        </div>

      </div>

    </div>
  </div>

<script>
  (function(){
    const nameEl = document.getElementById('brand-name');
    const mask = document.getElementById('reveal-mask');
    const text = nameEl.textContent;
    nameEl.textContent = '';
    nameEl.style.opacity = '1';
    nameEl.style.color = '#7CFF3B';
    const chars = [];
    for(let i=0;i<text.length;i++){
      const sp = document.createElement('span');
      sp.textContent = text[i];
      sp.style.opacity = '0';
      sp.style.display = 'inline-block';
      sp.style.transform = 'translateY(6px)';
      sp.style.transition = 'all 220ms cubic-bezier(.2,.9,.3,1)';
      nameEl.appendChild(sp);
      chars.push(sp);
    }
    mask.style.background = 'linear-gradient(90deg, rgba(255,255,255,0.06), rgba(255,255,255,0.0))';
    mask.style.width = '110%';
    mask.style.left = '0';
    mask.style.transform = 'translateX(-100%)';
    mask.style.transition = 'transform 700ms cubic-bezier(.2,.9,.3,1)';
    setTimeout(()=>{
      mask.style.transform = 'translateX(0%)';
      setTimeout(()=>{
        chars.forEach((c, i) => {
          setTimeout(()=>{
            c.style.opacity='1';
            c.style.transform='translateY(0px)';
            c.style.color = '#7CFF3B';
          }, i*60);
        });
        setTimeout(()=> mask.style.transform = 'translateX(100%)', chars.length*60 + 160);
      }, 420);
    }, 650);

    async function loadStats(){
      try {
        const r = await fetch('/get_shares');
        if(!r.ok) throw new Error('no data');
        const data = await r.json();
        const arr = data.shares_registrados || [];
        document.getElementById('cust-count').textContent = [...new Set(arr.map(x=>x.custodian_id))].length || 0;
        if(arr.length){
        const last = arr[arr.length-1];
        document.getElementById('last-sync').textContent = new Date(last.timestamp).toUTCString();
        } 
        else {
  document.getElementById('last-sync').textContent = 'Ninguna por ahora';
}
      } catch(e){
        document.getElementById('last-sync').textContent = 'offline';
      }
    }
    setTimeout(loadStats, 900);
  })();
</script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

# -------------------------------------------------------------
# ENDPOINTS DE API
# -------------------------------------------------------------
@app.post("/register_custodian", tags=["Custodios"])
def register_custodian(data: Custodian):
    if data.custodian_id in custodians:
        raise HTTPException(status_code=400, detail="El custodio ya está registrado.")
    custodians[data.custodian_id] = data.password
    return {"message": f"✅ Custodio '{data.custodian_id}' registrado correctamente."}


@app.post("/submit_share", tags=["Shares"])
def submit_share(data: Share):
    if data.custodian_id not in custodians:
        raise HTTPException(status_code=404, detail="Custodio no registrado.")
    if custodians[data.custodian_id] != data.password:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta.")

    share_hash = hashlib.sha256(data.share_data.encode()).hexdigest()

    shares.append({
        "custodian_id": data.custodian_id,
        "share_data": data.share_data,
        "share_hash": share_hash,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

    return {
        "message": "✅ Share recibido y almacenado correctamente.",
        "hash_generado": share_hash
    }


@app.get("/get_shares", tags=["Consulta"] )
def get_shares():
    return {"shares_registrados": shares}
