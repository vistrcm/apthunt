"""lambda created to get some urls as input, retrieve URL content, parse it and save."""

import logging
import json

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)


def respond(err, res=None):
    """helper function to create valid proxy object for AWS lambda + proxy gateway"""
    return {
        'statusCode': '400' if err else '200',
        'body': str(err) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def parse_body(body):
    """parse request body. return restulting dict.

    request body should be in format of lines
    key1: value1
    key2: value2
    ...

    returns same in form of dict"""

    result = {}
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        key, value = line.split(":")
        result[key] = value.strip()
    return result


def handler(event, context):
    """request handler"""
    LOGGER.debug(context)
    LOGGER.debug(event)

    if (event["body"] is None) or (not event["body"]):
        return respond(ValueError("looks like body is empty"))

    data = parse_body(event["body"])
    LOGGER.info("data: %s", data)
    return respond(None, event)
