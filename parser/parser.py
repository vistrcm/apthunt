"""lambda created to get some urls as input, retrieve URL content, parse it and save."""

import logging
import json
from datetime import datetime
import uuid
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

DYNAMO = boto3.client('dynamodb')
TABLE = DYNAMO.Table('apthunt')


def respond(err, res=None):
    """helper function to create valid proxy object for AWS lambda + proxy gateway"""
    return {
        'statusCode': '400' if err else '200',
        'body': str(err) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def handler(event, context):
    """request handler

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body. Some requests may be disabled.

    expecting request body to be similar to
    {
        "FeedTitle": "{{FeedTitle}}",
        "FeedUrl": "{{FeedUrl}}",
        "PostTitle": "{{PostTitle}}",
        "PostUrl": "{{PostUrl}}",
        "PostContent": "{{PostContent}}",
        "PostPublished": "{{PostPublished}}"
    }
    """
    LOGGER.debug("context: %s", context)
    LOGGER.debug("event: %s", json.dumps(event, indent=4))

    operations = {
        # disable some operations
        # 'DELETE': lambda dynamo, x: dynamo.delete_item(**x),
        # 'PUT': lambda dynamo, x: dynamo.update_item(**x),
        'GET': lambda x: TABLE.scan(**x),
        'POST': put_item,
    }
    body = event['body']

    LOGGER.debug("body: %s", body)

    operation = event['httpMethod']
    if operation in operations:
        payload = event['queryStringParameters'] if operation == 'GET' else json.loads(body)
        return respond(None, operations[operation](payload))

    return respond(ValueError('Unsupported method "{}"'.format(operation)))


def put_item(item):
    """put item into dynamodb table.

    will add fields `added` and `intid`.
    `added` equals to current time.
    `intid` - generated uuid4 working as primary key."""
    # extend a little bit
    item["added"] = datetime.utcnow()
    item["intid"] = uuid.uuid4()

    return TABLE.put_item(Item=item)


def scan(query):
    """scan table for items"""
    return TABLE.scan(query)
