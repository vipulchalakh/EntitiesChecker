from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import spacy
from collections import Counter
from typing import List

app = FastAPI()

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
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.body.get_text(separator=" ", strip=True) if soup.body else ""
    doc = nlp(text)
    entities = [(ent.text.strip(), ent.label_) for ent in doc.ents if ent.text.strip()]
    counter = Counter(entities)
    report = [EntityReport(term=term, entity_type=etype, count=count) for (term, etype), count in counter.items()]
    return sorted(report, key=lambda x: (-x.count, x.entity_type, x.term))

@app.get("/entities")
def get_entities_info():
    return {"detail": "Method Not Allowed. Please use POST to this endpoint with a JSON body: {\"url\": \"https://example.com\"}"} 