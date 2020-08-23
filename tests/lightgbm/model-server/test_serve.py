from unittest import TestCase

from serve import Model


class TestModelServer(TestCase):
    def test_validate(self):
        m = Model()
        result = m.validate(http_body=str([[i for i in range(66)]]))
        self.assertIn("result", result)
        self.assertIn("prediction_id", result)
        self.assertEqual(len(result["prediction_id"].split("/")), 3)
        self.assertEqual(result["result"], [0.9793770021409441])
