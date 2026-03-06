import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, Field
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = DATA_DIR / "index.json"

app = FastAPI(title="COPD-KB-PoC")


class AskReq(BaseModel):
    question: str = Field(..., min_length=2)
    top_k: int = Field(4, ge=1, le=10)
    audience: str = Field("doctor", description="doctor | patient")


@dataclass
class Chunk:
    source: str
    page: int
    text: str


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def chunk_text(text: str, size: int = 700, overlap: int = 120) -> List[str]:
    text = normalize_text(text)
    if not text:
        return []
    chunks: List[str] = []
    i = 0
    step = max(1, size - overlap)
    while i < len(text):
        chunks.append(text[i:i + size])
        i += step
    return chunks


def extract_terms(question: str) -> List[str]:
    q = normalize_text(question)
    terms = set()

    # ASCII tokens
    for t in re.findall(r"[A-Za-z0-9]{2,}", q):
        terms.add(t.lower())

    # Chinese continuous blocks -> 2/3-gram keywords
    zh_blocks = re.findall(r"[\u4e00-\u9fff]{2,}", q)
    for block in zh_blocks:
        if len(block) <= 3:
            terms.add(block)
        else:
            for n in (2, 3):
                for i in range(0, len(block) - n + 1):
                    terms.add(block[i:i + n])

    # fallback whole question
    if not terms:
        terms.add(q)

    return sorted(terms)


def load_index() -> Dict[str, Any]:
    if INDEX_FILE.exists():
        return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    return {"chunks": [], "docs": []}


def save_index(index: Dict[str, Any]) -> None:
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def scan_pdfs() -> List[Path]:
    return sorted(ROOT.glob("*.pdf"))


def ingest_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    reader = PdfReader(str(pdf_path))
    chunks_meta: List[Dict[str, Any]] = []
    for page_no, page in enumerate(reader.pages, start=1):
        text = normalize_text(page.extract_text() or "")
        if not text:
            continue
        for c in chunk_text(text):
            chunks_meta.append({
                "source": pdf_path.name,
                "page": page_no,
                "text": c,
            })
    return chunks_meta


def score_chunk(chunk_text_value: str, terms: List[str]) -> int:
    txt = chunk_text_value.lower()
    score = 0
    for t in terms:
        t_norm = t.lower()
        if t_norm in txt:
            # cap a term's contribution
            score += min(3, txt.count(t_norm))
    return score


def retrieve(question: str, top_k: int = 4) -> List[Dict[str, Any]]:
    idx = load_index()
    chunks = idx.get("chunks", [])
    if not chunks:
        return []

    terms = extract_terms(question)
    scored = []
    for c in chunks:
        s = score_chunk(c["text"], terms)
        if s > 0:
            scored.append((s, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    result = []
    for s, c in top:
        result.append({
            "score": s,
            "source": c["source"],
            "page": c["page"],
            "snippet": c["text"][:220]
        })
    return result


def build_answer(question: str, evidence: List[Dict[str, Any]], audience: str) -> str:
    if not evidence:
        return "当前知识库中暂无相关依据。"

    # concise and structured answer
    sources = []
    for e in evidence:
        key = f"{e['source']} p.{e['page']}"
        if key not in sources:
            sources.append(key)

    tone = "专业说明" if audience == "doctor" else "通俗说明"
    basis = "；".join([f"[{e['source']} p.{e['page']}] {e['snippet'][:60]}" for e in evidence[:3]])

    return (
        f"结论（{tone}）：基于当前知识库检索到的证据，问题“{question}”可从已收录文档得到支持性信息。\n"
        f"依据：{basis}\n"
        f"来源：{"; ".join(sources)}"
    )


@app.get('/health')
def health():
    idx = load_index()
    return {
        "ok": True,
        "index_exists": INDEX_FILE.exists(),
        "chunk_count": len(idx.get("chunks", [])),
        "doc_count": len(idx.get("docs", []))
    }


@app.post('/ingest')
def ingest():
    pdfs = scan_pdfs()
    if not pdfs:
        return {"ok": False, "message": "未找到PDF文件", "indexed_docs": 0, "chunks": 0}

    all_chunks: List[Dict[str, Any]] = []
    docs = []

    for p in pdfs:
        chunks = ingest_pdf(p)
        all_chunks.extend(chunks)
        docs.append({"name": p.name, "chunks": len(chunks)})

    index = {
        "docs": docs,
        "chunks": all_chunks
    }
    save_index(index)

    return {
        "ok": True,
        "indexed_docs": len(docs),
        "chunks": len(all_chunks),
        "docs": docs,
        "index_file": str(INDEX_FILE)
    }


@app.post('/ask')
def ask(req: AskReq):
    evidence = retrieve(req.question, req.top_k)

    if not evidence:
        return {
            "ok": True,
            "answer": "当前知识库中暂无相关依据。",
            "sources": [],
            "evidence": []
        }

    answer = build_answer(req.question, evidence, req.audience)
    sources = [{"doc": e["source"], "page": e["page"]} for e in evidence]

    return {
        "ok": True,
        "answer": answer,
        "sources": sources,
        "evidence": evidence
    }
