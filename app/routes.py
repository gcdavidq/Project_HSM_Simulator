from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import hashlib

router = APIRouter()

# almacenamiento temporal (simulación de DB)
custodians: Dict[str, dict] = {}
shares: List[dict] = []

# modelos de entrada
class CustodianRegister(BaseModel):
    custodian_id: str
    password: str

class ShareInput(BaseModel):
    custodian_id: str
    share_data: str
    share_hash: str

@router.post("/register_custodian")
def register_custodian(data: CustodianRegister):
    """Registrar un custodio"""
    if data.custodian_id in custodians:
        raise HTTPException(status_code=400, detail="Custodio ya registrado")

    custodians[data.custodian_id] = {
        "id": data.custodian_id,
        "password": data.password
    }
    return {"message": f"Custodio {data.custodian_id} registrado correctamente"}

@router.post("/submit_share")
def submit_share(data: ShareInput):
    """Recibir una parte (share) del custodio"""
    if data.custodian_id not in custodians:
        raise HTTPException(status_code=404, detail="Custodio no registrado")

    # Verificar hash de comprobación
    computed_hash = hashlib.sha256(data.share_data.encode()).hexdigest()
    if computed_hash != data.share_hash:
        raise HTTPException(status_code=400, detail="Hash no coincide")

    shares.append(data.dict())
    total = len(shares)
    return {
        "message": f"Share recibido de {data.custodian_id}",
        "total_shares_recibidos": total
    }
