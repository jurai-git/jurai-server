import flask
import numpy as np
from flask import jsonify
from models.utils import *


def args_inference(model, tokenizer, text) -> flask.jsonify:
    summaries = summarize(text, model, tokenizer)
    return jsonify(args=summaries)


def prob_inference(model, tokenizer, text) -> flask.jsonify:
    prediction = model.predict(
        preprocess_text(text, tokenizer, 900)
    )

    class_labels = {
        0: 'positive',
        1: 'partial',
        2: 'negative',
    }

    predicted_class = class_labels[np.argmax(prediction[0])]
    predictions_dict = {class_labels[idx]: float(prediction[0][idx]) for idx in range(len(class_labels))}

    return jsonify(
        {
            'input': text,
            'predicted_class': predicted_class,
            'probabilities': predictions_dict,
        }
    )
