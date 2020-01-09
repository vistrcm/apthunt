import json
import random
import time
import unittest
from decimal import Decimal
from json.decoder import JSONDecodeError

import boto3
from aws_xray_sdk import global_sdk_config
from moto import mock_sqs

from clparser import parse_request_body
from handler import prepare4dynamo, que_thumbs

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

    def test_que_thumbs_none_thumbs(self):
        test_data = {
            "thumbs": None,
        }
        # only logs here
        with self.assertLogs() as cm:
            que_thumbs(None, None, test_data)
            self.assertEqual(cm.output, ['INFO:root:no thumbs found'])

    @mock_sqs()
    def test_que_thumbs_thumbs(self):
        # Create SQS client
        sqs_client = boto3.client('sqs', region_name="us-east-1")
        queue_url = sqs_client.create_queue(
            QueueName='test'
        )['QueueUrl']

        test_data = {
            "thumbs": [
                "t1",
                "2",
                "3"
            ],
        }

        expected = ['INFO:root:thumb SQS response message id:'] # 3 elements with similar start
        # only logs here
        with self.assertLogs() as cm:
            que_thumbs(sqs_client, queue_url, test_data)
            for i, elem in enumerate(expected):
                self.assertIn(elem, cm.output[i])

        time.sleep(1)  # sleep a little to get all messages... not sure if it really helps
        messages = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=4)[
            "Messages"
        ]
        received = []
        for m in messages:
            received.extend(json.loads(m["Body"]))

        self.assertEqual(set(received), set(test_data["thumbs"]))


if __name__ == '__main__':
    unittest.main()
