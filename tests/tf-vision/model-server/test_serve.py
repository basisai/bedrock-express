from unittest import TestCase

from serve import Model


class TestModelServer(TestCase):
    def test_validate(self):
        m = Model()
        with open("./tests/208.jpg", "rb") as f:
            m.validate(http_body=None, files={"image": f})
