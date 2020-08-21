import json
import random
import unittest
from json.decoder import JSONDecodeError

from aws_xray_sdk import global_sdk_config
from requests_html import HTML

from clparser import parse_request_body, get_bedrooms, parse_price

global_sdk_config.set_sdk_enabled(False)


class TestParser(unittest.TestCase):
    def test_parse_price(self):
        doc = 'xxxxxx<span class="price">$2,895</span> xxxxxxx'
        self.assertEqual(parse_price(HTML(html=doc)), {'price_text': '$2,895', 'price': 2895})

    def test_get_bedrooms_full(self):
        self.assertEqual(get_bedrooms("'2br - 1000ft2'"), 2.0)

    def test_get_bedrooms_no_area(self):
        self.assertEqual(get_bedrooms("1br"), 1.0)

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


if __name__ == '__main__':
    unittest.main()
