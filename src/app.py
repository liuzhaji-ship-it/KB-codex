from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="COPD-KB-PoC")

class AskReq(BaseModel):
    question: str

@app.get('/health')
def health():
    return {"ok": True, "stage": "coding_started"}

@app.post('/ingest')
def ingest():
    # TODO: implement PDF ingestion for the 3 local files
    return {
        "ok": True,
        "message": "ingest pipeline scaffold created"
    }

@app.post('/ask')
def ask(req: AskReq):
    # TODO: implement retrieval + citation answer generation
    return {
        "ok": True,
        "answer": "当前知识库中暂无相关依据。",
        "sources": []
    }
