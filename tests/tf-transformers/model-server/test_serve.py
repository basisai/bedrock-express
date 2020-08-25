from unittest import TestCase

from serve import Model


class TestModelServer(TestCase):
    def test_validate(self):
        m = Model()
        result = m.validate(http_body='{"query": "Bedrock is amazing!"}', skip_preprocess=True)
        self.assertIn("result", result)
        self.assertIn("prediction_id", result)
        self.assertEqual(len(result["prediction_id"].split("/")), 3)
        self.assertEqual(result["result"], [{"POSITIVE": 0.9998825788497925}])
