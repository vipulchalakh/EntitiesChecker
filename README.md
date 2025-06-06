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

## Deployment to Vercel

### Option 1: Deploy from the Vercel Dashboard

1. Fork or clone this repository to your GitHub account
2. Log in to [Vercel](https://vercel.com)
3. Click "New Project"
4. Import your GitHub repository
5. Keep the default settings and click "Deploy"

### Option 2: Deploy with Vercel CLI

1. Install the Vercel CLI: `npm i -g vercel`
2. Run `vercel login` and follow the prompts
3. Navigate to the project directory
4. Run `vercel` to deploy

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