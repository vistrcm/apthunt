"""lambda created to get some urls as input, retrieve URL content, parse it and save."""
import json
import logging
import os
import uuid
from datetime import datetime
from decimal import Decimal
from json.decoder import JSONDecodeError

import boto3
from aws_xray_sdk.core import patch
from aws_xray_sdk.core import xray_recorder
from clparser import parse_request_body, parse_page, PostRemovedException, CL404Exception

# x-ray tracing
patch(['boto3'])

LOGGER = logging.getLogger()
if os.environ.get("LOG_LEVEL", "INFO") == "DEBUG":
    LOGGER.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.INFO)

# Quick sanity checks and predefined local dev
if os.getenv("AWS_SAM_LOCAL", ""):
    DYNAMO = boto3.resource('dynamodb', endpoint_url="http://dynamodb:8000")
else:
    DYNAMO = boto3.resource('dynamodb')
TABLE = DYNAMO.Table(os.getenv("TABLE_NAME", "apthunt"))

# Create SQS client
SQS = boto3.client('sqs')
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL", "")


def respond(err, res=None, code=400):
    """helper function to create valid proxy object for AWS lambda + proxy gateway"""
    return {
        'statusCode': str(code) if err else '200',
        'body': str(err) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


@xray_recorder.capture('handler')
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

    operation = event['httpMethod']
    if operation not in operations:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))

    raw_body = event['body']

    LOGGER.debug("raw_body: '%s'", raw_body)
    try:
        body = parse_request_body(raw_body)
    except JSONDecodeError as ex:
        msg = "Could not parse body. Ex: '{}'".format(ex)
        LOGGER.warning(msg)
        return respond(ValueError(msg))
    LOGGER.debug("body: '%s'", body)

    payload = event['queryStringParameters'] if operation == 'GET' else body
    try:
        resp = operations[operation](payload)
    except Exception as ex:  # pylint: disable=broad-except
        msg = "got exception doing '{}' on with '{}': {}".format(operations[operation], payload, ex)
        LOGGER.warning(msg, exc_info=True)
        return respond(ValueError(msg), code=500)

    LOGGER.info("operation %s response: '%s'", operation, resp)
    return respond(None, resp)


@xray_recorder.capture('prepare4dynamo')
def prepare4dynamo(item):
    """Need some preparation before sending item to the dynamodb"""
    processed = {}
    for key, value in item.items():
        # convert floats to Decimal
        # interesting conversion to string and to Decimal required according to the documentation
        # "To create a Decimal from a float, first convert it to a string."
        # see https://docs.python.org/3.1/library/decimal.html
        if isinstance(value, float):
            processed[key] = Decimal(str(value))
        else:
            processed[key] = value
    return processed


@xray_recorder.capture('que_thumbs')
def que_thumbs(item):
    """send item thumbs to the SQS queue"""
    # Send message to SQS queue
    for thumbs in item.get("thumbs"):
        response = SQS.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=thumbs
        )
        LOGGER.info("thumb SQS response message id: %s", response['MessageId'])


@xray_recorder.capture('put_item')
def put_item(item):
    """put item into dynamodb table.

    will add fields `added` and `intid`.
    `added` equals to current time (unixtime in ms).
    `intid` - generated uuid4 working as primary key."""
    # extend a little bit
    post_url = item["PostUrl"]
    item["added"] = int(datetime.utcnow().timestamp() * 1000)
    item["intid"] = uuid.uuid4().hex

    # parse_page can throw PostRemovedException
    # this means post removed. No need to proceed.
    try:
        parsed = parse_page(post_url)
        que_thumbs(parsed)
    except (PostRemovedException, CL404Exception):
        LOGGER.info("Post removed: %s", post_url)
        return {"message": "post removed", "item": item}

    # extend item with parsed data
    for key, value in parsed.items():
        item["parsed_" + key] = value

    processed_item = prepare4dynamo(item)
    return TABLE.put_item(Item=processed_item)


def scan(query):
    """scan table for items"""
    return TABLE.scan(query)
