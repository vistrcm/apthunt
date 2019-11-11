import json
import random
import unittest
from decimal import Decimal
from json.decoder import JSONDecodeError

from aws_xray_sdk import global_sdk_config
from clparser import parse_request_body
from handler import prepare4dynamo

global_sdk_config.set_sdk_enabled(False)


class TestParser(unittest.TestCase):

    def test_parse_body_empty(self):
        with self.assertRaises(JSONDecodeError):
            parse_request_body("")

    def test_parse_body_simple(self):
        self.assertEqual(parse_request_body("{}"), {})

    def test_parse_body_some_defined_dict(self):
        self.assertEqual(parse_request_body(
            '{"c": "d", "a": "b", "1": "2", "y": 23234}'),
            {"a": "b", "c": "d", "y": 23234,
             "1": "2"})

    def test_parser_body_random_dict(self):
        td = {}
        for _ in range(random.randint(1, 111)):
            k = str(random.random())
            v = random.random()
            td[k] = v
        data = json.dumps(td)
        self.assertEqual(parse_request_body(data), td)


class TestHandler(unittest.TestCase):
    def test_prepare4dynamo(self):
        test_data = {"string": "string", "int": 1, "float": random.random() * random.randint(-100, 100)}
        processed = prepare4dynamo(test_data)

        self.assertIsInstance(processed["float"], Decimal)


if __name__ == '__main__':
    unittest.main()
