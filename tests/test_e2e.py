from os import getenv
from unittest import TestCase

from requests import Session
from requests.exceptions import HTTPError


def get_inference_count(body: str) -> int:
    start = body.index("inference_value_count")
    end = body.index("\n", start)
    return int(float(body[start:end].split(" ")[-1]))


class TestModelServer(TestCase):
    def setUp(self):
        host = getenv("HOST", "localhost")
        port = getenv("PORT", "8080")
        self.url = f"http://{host}:{port}"

    def test_get(self):
        with Session() as s:
            resp = s.get(self.url)
            self.assertRaises(HTTPError, resp.raise_for_status)

    def test_post(self):
        with Session() as s:
            resp = s.get(f"{self.url}/metrics")
            resp.raise_for_status()
            before = get_inference_count(resp.text)

            for i in range(4):
                resp = s.post(self.url, json=[i for i in range(66)])
                resp.raise_for_status()
                result = resp.json()
                self.assertIn("result", result)
                self.assertIn("prediction_id", result)
                self.assertEqual(len(result["prediction_id"].split("/")), 3)
                self.assertEqual(result["result"], 0.9793770021409441)

            # Verify that metrics sum up correctly
            resp = s.get(f"{self.url}/metrics")
            resp.raise_for_status()
            after = get_inference_count(resp.text)
            self.assertEqual(after - before, 4)
