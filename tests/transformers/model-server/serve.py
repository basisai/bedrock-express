"""
Script for serving.
"""
import json

from bedrock_client.bedrock.model import BaseModel
from transformers import pipeline


class Model(BaseModel):
    def __init__(self):
        # Pretrained pipeline for sentiment analysis
        self.model = pipeline("sentiment-analysis")

    def pre_process(self, http_body, files):
        return json.loads(http_body)["query"]

    def predict(self, features: str):
        # Original score is absolute value denoting confidence
        return [{sample["label"]: sample["score"]} for sample in self.model(features)]
