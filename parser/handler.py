"""lambda created to get some urls as input, retrieve URL content, parse it and save."""
import copy
import hashlib
import json
import logging
import os
from datetime import datetime
from decimal import Decimal
from json.decoder import JSONDecodeError

import boto3
from aws_xray_sdk.core import patch  # type: ignore
from aws_xray_sdk.core import xray_recorder  # type: ignore

from clparser import parse_request_body, parse_page, PostRemovedException, CL404Exception

# x-ray tracing
patch(['boto3', 'botocore'])

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

# client to processor
SQS_PR = boto3.client('sqs')
SQS_PR_QUEUE_URL = os.getenv("PROCESSOR_SQS_QUEUE_URL", "")


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
        LOGGER.error(msg, exc_info=True)
        # return respond(ValueError(msg), code=500)
        raise ValueError(msg) from ex

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


@xray_recorder.capture('send_2_processor')
def send_2_processor(sqs, sqs_queue, item):
    """send item to the processor SQS"""
    msg = {
        "latitude": item["parsed_data_latitude"],
        "longitude": item["parsed_data_longitude"],
        "district": item["parsed_district"],
        "housing": item["parsed_housing"],
        "bedrooms": item["parsed_bedrooms"],
        "area": item["parsed_area"],
        "type": item["parsed_type"],
        "catsok": item["parsed_catsok"],
        "dogsok": item["parsed_dogsok"],
        "garagea": item["parsed_garagea"],
        "garaged": item["parsed_garaged"],
        "furnished": item["parsed_furnished"],
        "laundryb": item["parsed_laundryb"],
        "laundrys": item["parsed_laundrys"],
        "wd": item["parsed_wd"],
        "nthumbs": item["parsed_nthumbs"],
        'price': item["parsed_price"],
        'url': item["PostUrl"],
    }
    msg = json.dumps(msg)
    response = sqs.send_message(
        QueueUrl=sqs_queue,
        MessageBody=msg
    )
    LOGGER.info("processor SQS response message id: %s", response['MessageId'])


def get_md5(data):
    """calculate 'md5' for the data structure

    Go deep into dict and lists by calculating md5 for keys and values. Not sorted lists.
    """
    data_hash = hashlib.md5()

    if isinstance(data, dict):
        for key in sorted(data.keys()):
            data_hash.update(key.encode('utf8'))
            data_hash.update(get_md5(data[key]).digest())
    elif isinstance(data, list):
        for val in data:
            data_hash.update(get_md5(val).digest())
    elif isinstance(data, str):
        data_hash.update(data.encode('utf-8'))
    else:
        data_hash.update(str(data).encode('utf8'))

    return data_hash


def generate_id(item):
    """generate id for the item"""
    # let's create copy of item to exclude URL from getting md5
    new = copy.deepcopy(item)
    del new["PostUrl"]

    gen_id = get_md5(new)
    LOGGER.debug("generated id '%s' for the item: %s", gen_id, item)
    return gen_id.hexdigest()


@xray_recorder.capture('item_exist')
def item_exist(table, item):
    """check if item exist in dynamo table"""

    key = {'intid': item["intid"]}
    item = table.get_item(Key=key, ProjectionExpression='intid')

    return "Item" in item.keys()


@xray_recorder.capture('put_item')
def put_item(item):
    """put item into dynamodb table.

    will add fields `added` and `intid`.
    `added` equals to current time (unixtime in ms).
    `intid` - generated uuid4 working as primary key."""
    # extend a little bit
    post_url = item["PostUrl"]

    # parse_page can throw PostRemovedException
    # this means post removed. No need to proceed.
    try:
        parsed = parse_page(post_url)
    except (PostRemovedException, CL404Exception):
        LOGGER.info("Post removed: %s", post_url)
        return {"message": "post removed", "item": item}

    que_thumbs(SQS, SQS_QUEUE_URL, parsed)

    # extend item with parsed data
    for key, value in parsed.items():
        item["parsed_" + key] = value

    item["intid"] = generate_id(item)
    item["added"] = int(datetime.utcnow().timestamp() * 1000)

    if item_exist(TABLE, item):
        LOGGER.info("duplicate post: %s, %s", item["intid"], item["PostUrl"])
        return {"duplicate": item}

    processed_item = prepare4dynamo(item)
    dynamo_res = TABLE.put_item(Item=processed_item)
    send_2_processor(SQS_PR, SQS_PR_QUEUE_URL, item)
    return dynamo_res
