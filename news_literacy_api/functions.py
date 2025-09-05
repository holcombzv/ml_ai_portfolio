import tensorflow as tf
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def get_article_text(html_text):
    try:
        soup = BeautifulSoup(html_text, 'html.parser')

        article_text = []

        # Step 1: Try <article> tag
        article_tag = soup.find('article')
        if article_tag:
            paragraphs = article_tag.find_all('p')
            article_text = [clean_text(p.get_text(strip=True)) for p in paragraphs if p.get_text(strip=True)]
            if article_text:
                return article_text

        # Step 2: Try common container patterns (site-specific fallbacks)
        candidates = [
            {"name": "div", "attrs": {"class": "article-body"}},
            {"name": "section", "attrs": {"name": "articleBody"}},
            {"name": "div", "attrs": {"property": "articleBody"}},
            {"name": "div", "attrs": {"class": "Article__content"}},
        ]
        for cand in candidates:
            container = soup.find(cand["name"], cand["attrs"])
            if container:
                paragraphs = container.find_all('p')
                article_text = [clean_text(p.get_text(strip=True)) for p in paragraphs if p.get_text(strip=True)]
                if article_text:
                    return article_text

        # Step 3: Fallback → all <p> tags, but filter out junk
        bad_classes = ['caption', 'credit', 'advertisement', 'footer']
        for p in soup.find_all('p'):
            if not any(cls in (p.get('class') or []) for cls in bad_classes):
                text = p.get_text(strip=True)
                if text:
                    article_text.append(clean_text(text))

        return article_text  # Always return a list (may be empty)

    except Exception as e:
        logger.exception(f'Error: Could not retrieve article text: {e}')
        return []

def split_paragraphs(text: str):
    paragraphs = text.splitlines()
    for paragraph in paragraphs:
        paragraph = clean_text(paragraph)
    return paragraphs

def clean_text(text):
    try:
        text = text.lower()
        if '-' in text:
            text = text.split('-', 1)[1].strip()
        text = ''.join(char for char in text if char.isalnum() or char.isspace())
        return text
    except AttributeError:
        logger.exception(f'Input for clean_text has to be a string. Incorrect value: {text} Type: {type(text)}')
    except Exception as e:
        logger.exception(f"Error cleaning text: {e} | Input: {text}")

# Use model on scraped text
def evaluate_text(text, model, tokenizer, max_len=1000):
    sequence = tokenizer.texts_to_sequences([text])  # Convert text to sequence
    padded_sequence = tf.keras.preprocessing.sequence.pad_sequences(sequence, maxlen=max_len)  # Pad to max_len
    
    result = float(model.predict(padded_sequence))
    return result

