from pathlib import Path
from unittest import TestCase

from serve import Model


class TestModelServer(TestCase):
    def test_validate(self):
        path = Path(__file__).parent.parent / "artefact" / "model.pkl"
        m = Model(path=path)
        features = list(range(m.model.n_features_))
        result = m.validate(http_body=str([features]))
        self.assertIn("result", result)
        self.assertIn("prediction_id", result)
        self.assertEqual(len(result["prediction_id"].split("/")), 3)
        self.assertEqual(result["result"], [0.9489560209860071])
