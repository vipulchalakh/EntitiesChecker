import uvicorn
from backend import app

# Export the app for Vercel

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
