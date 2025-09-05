from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import tensorflow as tf
import pickle
import logging

from functions import *
from classes import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Icon links for attribution: <a href="https://www.flaticon.com/free-icons/detective" title="detective icons">Detective icons created by Freepik - Flaticon</a>

model = tf.keras.models.load_model('model/fact_checker_trained.keras')
with open('model/fact_checker_tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

app = FastAPI()

# Enable CORS for frontend/extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["chrome-extension://<your-extension-id>"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input from frontend
class TextRequest(BaseModel):
    text: str

# Model output
class PredictionResponse(BaseModel):
    score: float
    label: str

@app.post("/predict", response_model=PredictionResponse)
async def evaluate_article(request: TextRequest):
    try:
        html = request.text
        article = Article(1, html)
        score = article.evaluate_article(model, tokenizer)
        label = 'Real' if score > .5 else 'Fake'

        return {
            "score": score,
            'label': label
        }
    except Exception as e:
        logger.exception(f'Error calling model: {e}')
        return JSONResponse(
            status_code=500,
            content={"error": f"Model error: {str(e)}"}
        )

@app.get("/")
async def root():
    return {"message": "Fake News Detection API is running!"}
