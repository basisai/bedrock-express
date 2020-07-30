import json
import pickle
from typing import AnyStr, List, Mapping, Optional


def pre_process(http_body: AnyStr, files: Optional[Mapping[str, AnyStr]] = None) -> List[float]:
    array = json.loads(http_body)
    return [float(x) for x in array]


def post_process(scores: List[List[float]]) -> float:
    return scores[0][0]


class Model:
    def __init__(self):
        with open("/artefact/model.pkl", "rb") as f:
            self.model = pickle.load(f)

    def predict(self, features: List[float]) -> List[List[float]]:
        return self.model.predict_proba([features])