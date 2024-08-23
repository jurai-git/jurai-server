import re
import pandas as pd
from pypdf import PdfReader
from keras.src.legacy.preprocessing.text import Tokenizer
from keras.src.utils import pad_sequences
from models.purify import PurifyScraper


def build_tokenizer_from_csv(csv_file, vocab_size, oov_token):
    texts = pd.read_csv(csv_file, usecols=['ementa'])['ementa'].tolist()
    tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
    tokenizer.fit_on_texts(texts)
    return tokenizer


def preprocess_text(text, tokenizer, max_len):
    text = PurifyScraper().clean_text(text)
    sequences = tokenizer.texts_to_sequences([text])
    return pad_sequences(sequences, maxlen=max_len, truncating='post', padding='post')


def summarize(text, model, tokenizer, input_text='retorne os melhores argumentos: ', max_length=1028, num_outputs=3):
    input_text += text
    input_ids = tokenizer.encode(input_text, return_tensors='pt', max_length=max_length, truncation=True)

    summary_ids = model.generate(
        input_ids,
        max_length=200,
        min_length=40,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True,
        num_return_sequences=num_outputs
    )
    return [tokenizer.decode(i, skip_special_tokens=True, clean_up_tokenization_spaces=True) for i in summary_ids]

