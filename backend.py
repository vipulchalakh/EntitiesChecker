from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import spacy
from collections import Counter
from typing import List, Dict
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

nlp = spacy.load("en_core_web_sm")

class URLRequest(BaseModel):
    url: str

class EntityReport(BaseModel):
    term: str
    entity_type: str
    count: int

@app.post("/entities", response_model=List[EntityReport])
def extract_entities(request: URLRequest):
    try:
        resp = requests.get(request.url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {e}")
    soup = BeautifulSoup(resp.text, "html.parser")
    # Remove scripts/styles
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.body.get_text(separator=" ", strip=True) if soup.body else ""
    doc = nlp(text)
    entities = [(ent.text.strip(), ent.label_) for ent in doc.ents if ent.text.strip()]
    counter = Counter(entities)
    report = [EntityReport(term=term, entity_type=etype, count=count) for (term, etype), count in counter.items()]
    return sorted(report, key=lambda x: (-x.count, x.entity_type, x.term))
