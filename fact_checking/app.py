from functions import clean_text, get_article_text, evaluate_text

import streamlit as st

from tensorflow.keras.models import load_model
import pickle

model = load_model('fact_checker_trained.keras')

with open('fact_checker_tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

url = st.text_input(
    'Paste article URL here',
    label_visibility = 'collapsed',
    placeholder = 'Paste article URL here'
)

col1, col2, col3 = st.columns([2,1,2])
if col2.button('Fact-check', use_container_width=True):
    text = get_article_text(url)

    # Check if the text returned is an error message
    if text.startswith("Error:"):
        st.markdown(f'<span style="color:red">{text}</span>', unsafe_allow_html=True)
    else:
        result = evaluate_text(text, model, tokenizer)

        if result < 0.5:
            st.markdown(f'<span style="color:red">Result: {round(result * 100, 1)}% - Most likely fake</span>', unsafe_allow_html=True)
        elif result < 0.85:
            st.markdown(f'<span style="color:orange">Result: {round(result * 100, 1)}% - Might be real</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span style="color:green">Result: {round(result * 100, 1)}% - Most likely real</span>', unsafe_allow_html=True)

