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


def handler(event, context):
    """request handler"""
    LOGGER.debug(context)
    LOGGER.debug(event)

    if (event["body"] is None) or (not event["body"]):
        return respond(ValueError("looks like body is empty"))

    post_url = event["body"].strip()

    LOGGER.info("post_url: %s", post_url)
    return respond(None, event)
