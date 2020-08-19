import pickle
from typing import List

from bedrock_client.bedrock.model import BaseModel


class Model(BaseModel):
    def __init__(self, path: str = "/artefact/model.pkl"):
        with open(path, "rb") as f:
            self.model = pickle.load(f)

    def predict(self, features: List[float]) -> float:
        return self.model.predict_proba([features])[:, 0].item()
