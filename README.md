# Entities Checker

A web application that extracts named entities from web pages using NLP.

## Features

- Extract named entities from any web page by URL
- Categorize entities by type (Person, Organization, Location, etc.)
- View results in table, chart, or insights format
- Export results to clipboard or CSV

## Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Download the spaCy model: `python -m spacy download en_core_web_sm`
6. Run the application: `python main.py`
7. Open your browser and navigate to `http://localhost:8000`

## Deployment on Vercel with Python Backend

This project is structured to work with Vercel's serverless functions for the Python backend. The backend code is located in the `api/` directory as required by Vercel.

- **Static files** (HTML, etc.) are in the project root.
- **Python backend** (FastAPI) is in `api/main.py` and `api/backend.py`.

### How it works
- Vercel serves static files from the root (e.g., `index.html`).
- API requests to `/api/main` are handled by FastAPI in `api/main.py`.

### Local Development
To run locally:
```bash
cd api
uvicorn main:app --reload
```

### Notes
- Make sure all Python dependencies are listed in `requirements.txt`.
- The backend expects the `en_core_web_sm` spaCy model to be installed.

## Project Structure

- `index.html` - Frontend interface
- `main.py` - Entry point for the application
- `backend.py` - FastAPI backend implementation
- `vercel.json` - Vercel deployment configuration

## Technologies Used

- Frontend: HTML, CSS, JavaScript
- Backend: FastAPI (Python)
- NLP: spaCy
- Deployment: Vercel