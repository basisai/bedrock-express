import pickle
from typing import List, Optional

from bedrock_client.bedrock.model import BaseModel


class Model(BaseModel):
    def __init__(self, path: Optional[str] = None):
        with open(path or "/artefact/model.pkl", "rb") as f:
            self.model = pickle.load(f)

    def predict(self, features: List[List[float]]) -> List[float]:
        return self.model.predict_proba(features)[:, 0].tolist()
