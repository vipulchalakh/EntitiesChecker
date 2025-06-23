from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
import spacy
from collections import Counter
from typing import List, Dict, Any, Optional
from starlette.middleware.cors import CORSMiddleware
import logging
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load spaCy model with optimized settings
try:
    logger.info("Attempting to load spaCy model...")
    nlp = spacy.load("en_core_web_sm", disable=["parser", "textcat"])
    logger.info("Successfully loaded spaCy model")
except Exception as e:
    logger.error(f"Error loading spaCy model: {str(e)}")
    raise

class URLRequest(BaseModel):
    url: str

class EntityReport(BaseModel):
    term: str
    entity_type: str
    count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "term": self.term,
            "entity_type": self.entity_type,
            "count": self.count
        }

@app.post("/entities", response_model=List[EntityReport])
async def extract_entities(request: URLRequest):
    try:
        logger.info(f"Processing request for URL: {request.url}")
        
        # Validate URL format
        if not request.url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid URL format. URL must start with http:// or https://")
        
        # Fetch the webpage
        try:
            logger.info("Fetching webpage...")
            resp = requests.get(request.url, timeout=10)
            resp.raise_for_status()
            logger.info("Successfully fetched webpage")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")
        
        # Parse the content
        try:
            logger.info("Parsing webpage content...")
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style"]):
                tag.decompose()
            text = soup.body.get_text(separator=" ", strip=True) if soup.body else ""
            
            if not text:
                logger.warning("No text content found in webpage")
                raise HTTPException(status_code=400, detail="No text content found in the webpage")
            
            logger.info(f"Extracted {len(text)} characters of text")
                
            # Process with spaCy
            logger.info("Processing text with spaCy...")
            doc = nlp(text)
            # Only include entity types relevant to Google's Knowledge Graph
            allowed_entity_types = {
                "PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE", "NORP", "FAC"
            }
            entities = [
                (ent.text.strip(), ent.label_)
                for ent in doc.ents
                if ent.text.strip() and ent.label_ in allowed_entity_types
            ]
            
            if not entities:
                logger.info("No entities found")
                return []
            
            logger.info(f"Found {len(entities)} entities")
                
            counter = Counter(entities)
            report = [EntityReport(term=term, entity_type=etype, count=count) 
                     for (term, etype), count in counter.items()]
            
            # Sort by count (descending), then entity type, then term
            sorted_report = sorted(report, key=lambda x: (-x.count, x.entity_type, x.term))
            
            logger.info(f"Successfully processed {len(sorted_report)} unique entities")
            return JSONResponse(content=[item.to_dict() for item in sorted_report])
            
        except Exception as e:
            logger.error(f"Error processing content: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error processing content: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/entities")
def get_entities_info():
    return JSONResponse(
        status_code=405,
        content={"detail": "Method Not Allowed. Please use POST to this endpoint with a JSON body: {\"url\": \"https://example.com\"}"},
        headers={"Content-Type": "application/json"}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port) 