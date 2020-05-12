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
    """request handler"""
    LOGGER.debug("context: %s", context)
    LOGGER.debug("event: %s", json.dumps(event, indent=4))

    raw_body = event['body']

    LOGGER.debug("raw_body: '%s'", raw_body)
    try:
        body = parse_request_body(raw_body)
    except JSONDecodeError as ex:
        msg = "Could not parse body. Ex: '{}'".format(ex)
        LOGGER.warning(msg)
        return respond(ValueError(msg))

    LOGGER.debug("body: '%s'", body)

    try:
        resp = put_item(body)
    except Exception as ex:  # pylint: disable=broad-except
        msg = "got exception doing put_item with '{}': {}".format(body, ex)
        LOGGER.warning(msg, exc_info=True)
        return respond(ValueError(msg), code=500)

    LOGGER.info("response: '%s'", resp)
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
def que_thumbs(sqs, sqs_queue, item):
    """send item thumbs to the SQS queue"""
    # Send message to SQS queue
    thumbs = item.get("thumbs")
    if thumbs is None:
        LOGGER.info("no thumbs found")
        return

    msg = json.dumps(thumbs)
    response = sqs.send_message(
        QueueUrl=sqs_queue,
        MessageBody=msg
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
        que_thumbs(SQS, SQS_QUEUE_URL, parsed)
    except (PostRemovedException, CL404Exception):
        LOGGER.info("Post removed: %s", post_url)
        return {"message": "post removed", "item": item}

    # extend item with parsed data
    for key, value in parsed.items():
        item["parsed_" + key] = value

    processed_item = prepare4dynamo(item)
    return TABLE.put_item(Item=processed_item)
