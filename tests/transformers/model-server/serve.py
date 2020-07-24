"""
Script for serving.
"""
import json

from transformers import pipeline


def pre_process(http_body, files):
    return json.loads(http_body)["query"]


class Model:
    def __init__(self):
        # Pretrained pipeline for sentiment analysis
        self.model = pipeline('sentiment-analysis')

    def predict(self, features):
        # Returns both label and score
        # e.g. {'label': 'POSITIVE', 'score': 0.93052536}
        return self.model(features)[0]
