from unittest import TestCase

from serve import Model


class TestModelServer(TestCase):
    def test_validate():
        m = Model()
        m.validate(http_body='{"query": "Good job"}')
