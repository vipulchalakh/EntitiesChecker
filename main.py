from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import spacy
from collections import Counter
from typing import List
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

# Serve static files (css, js, images) from /static
app.mount("/static", StaticFiles(directory=".", html=True), name="static")

# Serve index.html for the root path
@app.get("/")
def read_index():
    return FileResponse("index.html")

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

@app.get("/entities")
def get_entities_info():
    return JSONResponse(
        status_code=405,
        content={"detail": "Method Not Allowed. Please use POST to this endpoint with a JSON body: {\"url\": \"https://example.com\"}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000) 