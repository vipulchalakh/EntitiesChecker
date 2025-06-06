from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import spacy
from collections import Counter
from typing import List
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Serve static files from /static
app.mount("/static", StaticFiles(directory=".", html=True), name="static")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
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
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.body.get_text(separator=" ", strip=True) if soup.body else ""
    doc = nlp(text)
    entities = [(ent.text.strip(), ent.label_) for ent in doc.ents if ent.text.strip()]
    counter = Counter(entities)
    report = [EntityReport(term=term, entity_type=etype, count=count) for (term, etype), count in counter.items()]
    return sorted(report, key=lambda x: (-x.count, x.entity_type, x.term))

# Serve index.html for the root path
@app.get("/")
def read_index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000) 