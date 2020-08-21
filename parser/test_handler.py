import json
import random
import time
import unittest
from decimal import Decimal

import boto3
from moto import mock_sqs

from handler import get_md5, prepare4dynamo, que_thumbs


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

        expected = ['INFO:root:thumb SQS response message id:']  # 3 elements with similar start
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

    def test_get_md5_str(self):
        data = "a"
        # correct value calculated by
        # $ md5 -s a
        # MD5 ("a") = 0cc175b9c0f1b6a831c399e269772661
        self.assertEqual(get_md5(data).hexdigest(), "0cc175b9c0f1b6a831c399e269772661")

    def test_get_md5_int(self):
        data = 100500
        # correct value calculated by
        # $ md5 -s 100500
        # MD5 ("100500") = e745a6bad4ffe5a1b35aac134ea148c7
        self.assertEqual(get_md5(data).hexdigest(), "e745a6bad4ffe5a1b35aac134ea148c7")

    def test_get_md5_float(self):
        data = 1.056
        # correct value calculated by
        # $ md5 -s 100500
        # MD5 ("100500") = e745a6bad4ffe5a1b35aac134ea148c7
        self.assertEqual(get_md5(data).hexdigest(), "a50a79a1862f5ae748ed507f45f244bc")

    def test_get_md5_list_1(self):
        data = ["a", 100500, 1.056]
        self.assertEqual(get_md5(data).hexdigest(), "0023ec2e3fef8f649c130f22ea6b7820")

    def test_get_md5_list_2(self):
        data = [100500, "a", 1.056]
        self.assertEqual(get_md5(data).hexdigest(), "0943aa9c84423613b63eda3c18c02ce8")

    def test_get_md5_dict_1(self):
        data = {
            "a": 100500,
            "b": 1056,
            "c": ["ba", "bu", "nm"]
        }
        self.assertEqual(get_md5(data).hexdigest(), "e17234cd2697951f7e0116945d11d824")

    def test_get_md5_dict_2(self):
        data = {
            "c": ["ba", "bu", "nm"],
            "a": 100500,
            "b": 1056,
        }
        # note, different key order, but same digest as above
        self.assertEqual(get_md5(data).hexdigest(), "e17234cd2697951f7e0116945d11d824")

    def test_get_md5_dict_deep(self):
        data = {
            "c": ["ba", "bu", "nm"],
            "a": 100500,
            "b": {
                "c": ["ba", "bu", "nm"],
                "a": {
                    "c": {
                        "c": ["ba", "bu", "nm"],
                        "a": 100500,
                        "b": {
                            "c": ["ba", "bu", "nm"],
                            "a": 100500,
                            "b": 1056,
                        },
                    },
                    "a": 100500,
                    "b": 1056,
                },
                "b": 1056,
            }
        }
        # note, different key order, but same digest as above
        self.assertEqual(get_md5(data).hexdigest(), "e0614921e306095859c904e487c29f17")


if __name__ == '__main__':
    unittest.main()
