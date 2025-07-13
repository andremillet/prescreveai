from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import os

# Importar as funções de parsing e geração de PDF do prescreveai.py
# Assumimos que prescreveai.py está no mesmo diretório ou no PYTHONPATH
# Para evitar conflitos de nome, podemos importar com um alias
import prescreveai as cli_parser

app = FastAPI(
    title="PrescreveAI API",
    description="API para gerar prescrições médicas em formato JSON e PDF.",
    version="1.0.0",
)

# --- Modelos Pydantic para validação de dados ---

class Medication(BaseModel):
    nome: str
    dosagem: str
    comentario: Optional[str] = None
    posologia: str

class EmitterData(BaseModel):
    nome: str
    crm: str
    endereco: str
    telefone: str
    cidade_uf: str

class PrescriptionRequest(BaseModel):
    medication_string: str
    emitter_data: EmitterData
    template: str = "memed" # Default template

class PrescriptionResponse(BaseModel):
    medicacoes: List[Medication]
    pdf_filename: str

# --- Endpoint da API ---

@app.post("/prescribe", response_model=PrescriptionResponse)
async def prescribe(request: PrescriptionRequest):
    # Chamar a função de parsing do prescreveai.py
    parse_result = cli_parser.parse_medication_string(request.medication_string)

    if "error" in parse_result:
        raise HTTPException(status_code=400, detail=parse_result["error"])

    medications = parse_result["medicacoes"]

    # Temporariamente sobrescrever EMITTER_DATA para a geração do PDF
    # Em uma API real, os dados do emitente seriam passados diretamente para a função de geração de PDF
    # sem depender de uma variável global.
    cli_parser.EMITTER_DATA = request.emitter_data.dict()

    pdf_filename = ""
    if request.template == "memed":
        pdf_filename = "prescricao_memed.pdf"
        cli_parser.generate_memed_like_pdf(medications, filename=pdf_filename)
    elif request.template == "simple":
        pdf_filename = "prescricao_simple.pdf"
        cli_parser.generate_simple_pdf(medications, filename=pdf_filename)
    else:
        raise HTTPException(status_code=400, detail=f"Template desconhecido: {request.template}")

    # Limpar EMITTER_DATA após o uso para evitar vazamento de estado entre requisições
    cli_parser.EMITTER_DATA = {}

    return PrescriptionResponse(medicacoes=medications, pdf_filename=pdf_filename)

# --- Para executar o servidor (não faz parte do arquivo api_server.py, mas é como você o iniciaria) ---
# uvicorn api_server:app --reload --port 8000
