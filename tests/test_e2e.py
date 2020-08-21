from os import getenv
from typing import Optional
from unittest import TestCase, skipIf

from requests import Session
from requests.exceptions import HTTPError

MODELS = {
    "image": ["torchvision", "tf-vision"],
    "language": ["transformers", "tf-transformers"],
    "churn": ["lightgbm"],
}


def get_inference_count(body: str, label: Optional[int] = None) -> int:
    if label is not None:
        start = body.index(f'inference_value_total{{bin="{label}.0"}}')
    else:
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

    @skipIf(getenv("MODEL", None) not in MODELS["image"], "test upload on vision models")
    def test_file_upload(self):
        with Session() as s:
            resp = s.get(f"{self.url}/metrics")
            resp.raise_for_status()
            before = get_inference_count(resp.text, 208)

            resp = s.post(self.url, files={"image": open("208.jpg", "rb")})
            resp.raise_for_status()
            result = resp.json()
            self.assertIn("result", result)
            self.assertEqual(result["result"], [208])

            # Verify that metrics sum up correctly
            resp = s.get(f"{self.url}/metrics")
            resp.raise_for_status()
            after = get_inference_count(resp.text, 208)
            self.assertEqual(after - before, 1)

    @skipIf(getenv("MODEL", None) not in MODELS["language"], "post body for language models")
    def test_sentiment(self):
        with Session() as s:
            resp = s.get(f"{self.url}/metrics")
            resp.raise_for_status()
            before = get_inference_count(resp.text)

            for i in range(4):
                resp = s.post(self.url, json={"query": "Bedrock is amazing!"})
                resp.raise_for_status()
                result = resp.json()
                self.assertIn("result", result)
                self.assertIn("prediction_id", result)
                self.assertEqual(len(result["prediction_id"].split("/")), 3)
                self.assertEqual(result["result"], [{"POSITIVE": 0.9998825788497925}])

            # Verify that metrics sum up correctly
            resp = s.get(f"{self.url}/metrics")
            resp.raise_for_status()
            after = get_inference_count(resp.text)
            self.assertEqual(after - before, 4)

    @skipIf(
        getenv("MODEL", None) not in MODELS["churn"], "post body for churn prediction models",
    )
    def test_post(self):
        with Session() as s:
            resp = s.get(f"{self.url}/metrics")
            resp.raise_for_status()
            before = get_inference_count(resp.text)

            for i in range(4):
                resp = s.post(self.url, json=[[i for i in range(66)]])
                resp.raise_for_status()
                result = resp.json()
                self.assertIn("result", result)
                self.assertIn("prediction_id", result)
                self.assertEqual(len(result["prediction_id"].split("/")), 3)
                self.assertEqual(result["result"], [0.9793770021409441])

            # Verify that metrics sum up correctly
            resp = s.get(f"{self.url}/metrics")
            resp.raise_for_status()
            after = get_inference_count(resp.text)
            self.assertEqual(after - before, 4)
