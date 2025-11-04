from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import hashlib
from datetime import datetime

# -------------------------------------------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# -------------------------------------------------------------
app = FastAPI(
    title=" HSM Master Key Simulator API",
    description=(
        "API para registrar custodios y enviar shares de claves maestras. "
        "Cada share se valida, se genera su hash automáticamente y se almacena "
        "con un sello de tiempo para trazabilidad."
    ),
    version="1.4.0",
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

# -------------------------------------------------------------
# PÁGINA DE INICIO ANIMADA
# -------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, tags=["Inicio"])
def root():
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HSM Master Key Simulator</title>
        <style>
            body {
                margin: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
                color: white;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                text-align: center;
                overflow: hidden;
            }
            img {
                width: 120px;
                height: 120px;
                margin-bottom: 20px;
                animation: float 4s ease-in-out infinite;
            }
            h1 {
                font-size: 2.6em;
                background: linear-gradient(90deg, #00c6ff, #0072ff, #00c6ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-size: 200% auto;
                animation: shine 3s linear infinite;
                margin-bottom: 10px;
            }
            p {
                font-size: 1.2em;
                opacity: 0.9;
                margin-bottom: 35px;
                animation: fadeIn 2s ease-in-out;
            }
            .btn {
                display: inline-block;
                padding: 12px 25px;
                background-color: #00C6FF;
                border: none;
                border-radius: 10px;
                color: #fff;
                text-decoration: none;
                font-weight: bold;
                font-size: 1.1em;
                transition: background-color 0.3s, transform 0.3s;
                animation: fadeInUp 2s ease;
            }
            .btn:hover {
                background-color: #0072ff;
                transform: scale(1.07);
                box-shadow: 0px 0px 10px rgba(0, 198, 255, 0.7);
            }
            footer {
                position: absolute;
                bottom: 15px;
                font-size: 0.9em;
                opacity: 0.7;
                animation: fadeIn 3s ease;
            }

            /* Animaciones */
            @keyframes float {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
                100% { transform: translateY(0px); }
            }
            @keyframes shine {
                to { background-position: 200% center; }
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(30px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    </head>
    <body>
        <img src="https://cdn-icons-png.flaticon.com/512/4149/4149670.png" alt="Logo HSM">
        <h1>HSM Master Key Simulator</h1>
        <p>Bienvenido al sistema de gestión y validación de shares criptográficos.</p>
        <a href="/docs" class="btn">Ir a la Documentación</a>
        <footer>© 2025 Proyecto HSM | Desarrollado con FastAPI</footer>
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
    return {"message": f"Custodio '{data.custodian_id}' registrado correctamente."}


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
        "message": "Share recibido y almacenado correctamente.",
        "hash_generado": share_hash
    }


@app.get("/get_shares", tags=["Consulta"])
def get_shares():
    return {"shares_registrados": shares}
