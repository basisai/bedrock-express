from unittest import TestCase

from serve import Model


class TestModelServer(TestCase):
    def test_validate(self):
        m = Model()
        m.validate(http_body=str([[i for i in range(66)]]))
