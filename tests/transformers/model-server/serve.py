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

    def pre_process(self, http_body):
        return json.loads(http_body)["query"]

    def predict(self, features: str):
        # Original score is absolute value denoting confidence
        # Multiple by -1 depending on whether POSITIVE or NEGATIVE
        if self.model(features)[0]["label"] == "POSITIVE":
            return self.model(features)[0]["score"]
        else:
            return -self.model(features)[0]["score"]


if __name__ == "__main__":
    m = Model()
    m.validate(sample='{"query": "Good job"}')
