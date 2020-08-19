from unittest import TestCase

from serve import Model


class TestModelServer(TestCase):
    def test_validate():
        # m = Model(path="./tests/lightgbm/artefact/model.pkl")
        m = Model()
        m.validate(http_body=str([i for i in range(66)]))
