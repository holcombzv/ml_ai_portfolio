# Web Scraping

#%%
import urllib3
from bs4 import BeautifulSoup

def clean_text(text):
    text = text.lower()
    if '-' in text:
        text = text.split('-', 1)[1].strip()
    text = ''.join(char for char in text if char.isalnum() or char.isspace())
    return text

def get_title(url):
    http = urllib3.PoolManager()
    resp = http.request('GET', url)
    
    soup = BeautifulSoup(resp.data, 'html.parser')
    title = soup.find("title")
    
    return title.text if title else "No title found"


import urllib3
from bs4 import BeautifulSoup
import re

def get_article_text(url):
    # Validate URL format
    if not isinstance(url, str) or not re.match(r'^https?://', url):
        return "Error: Invalid URL. Please enter a valid website link."

    http = urllib3.PoolManager()

    try:
        # Attempt to make a request
        resp = http.request('GET', url)
        
        # Check if response is successful
        if resp.status != 200:
            return f"Error: Failed to retrieve article. HTTP Status Code: {resp.status}"

        soup = BeautifulSoup(resp.data, 'html.parser')

        article_text = []

        for tag in ["article", "story"]:
            article_body = soup.find_all(tag)
            if article_body:
                article_text.extend([clean_text(p.get_text(strip=True)) for p in article_body])

        # Plan B: Extract all <p> tags if no article/story tag is found
        if not article_text:
            article_body = soup.find_all('p')
            if article_body:
                article_text.extend([clean_text(p.get_text(strip=True)) for p in article_body])

        return "\n".join(article_text) if article_text else "No article text found."

    except urllib3.exceptions.MaxRetryError:
        return "Error: Unable to reach the website. Please check the URL and try again."

    except urllib3.exceptions.HTTPError as e:
        return f"Error: HTTP error occurred - {e}"

    except Exception as e:
        return f"Error: An unexpected error occurred - {e}"

# %%
# load fact checker and tokenization

from tensorflow.keras.models import load_model
import pickle

model = load_model('fact_checker_trained.keras')

with open('fact_checker_tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

# %%
# Use model on scraped text
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

def evaluate_text(text, model, tokenizer, max_len=1000):
    sequence = tokenizer.texts_to_sequences([text])  # Convert text to sequence
    padded_sequence = pad_sequences(sequence, maxlen=max_len)  # Pad to max_len
    
    result = float(model.predict(padded_sequence))
    return result
# %%
