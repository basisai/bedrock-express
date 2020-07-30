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
        self.model = pipeline("sentiment-analysis", framework="tf")

    def predict(self, features: str):
        # Original score is absolute value denoting confidence
        # Multiple by -1 depending on whether POSITIVE or NEGATIVE
        if self.model(features)[0]["label"] == "POSITIVE":
            return self.model(features)[0]["score"]
        else:
            return -self.model(features)[0]["score"]
