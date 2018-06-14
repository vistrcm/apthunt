import unittest
import random

from clparser import parse_request_body
import json
from json.decoder import JSONDecodeError

class TestParser(unittest.TestCase):

    def test_parse_body_empty(self):
        with self.assertRaises(JSONDecodeError):
                    parse_request_body("")

    def test_parse_body_simple(self):
        self.assertEqual(parse_request_body("{}"), {})

    def test_parse_body_some_defined_dict(self):
        self.assertEqual(parse_request_body('{"c": "d", "a": "b", "1": "2", "y": 23234}'), {"a": "b", "c": "d", "y": 23234, "1": "2"})

    def test_parser_body_random_dict(self):
        td = {}
        for _ in range(random.randint(1, 111)):
            k = str(random.random())
            v = random.random()
            td[k] = v
        data = json.dumps(td)
        self.assertEqual(parse_request_body(data), td)

if __name__ == '__main__':
    unittest.main()
