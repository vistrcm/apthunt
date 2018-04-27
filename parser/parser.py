"""lambda created to get some urls as input, retrieve URL content, parse it and save."""

import logging
import json

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)


def respond(err, res=None):
    """helper function to create valid proxy object for AWS lambda + proxy gateway"""
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def handler(event, _):
    """request handler"""
    LOGGER.debug(event)
    # print all keys in body
    LOGGER.debug("received keys: %s", [key for key in event["body"].keys()])
    LOGGER.debug("FeedTitle: %s", event["body"]["FeedTitle"])
    LOGGER.debug("FeedUrl: %s", event["body"]["FeedUrl"])
    LOGGER.debug("PostUrl: %s", event["body"]["PostUrl"])
    LOGGER.debug("PostContent: %s", event["body"]["PostContent"])
    LOGGER.debug("PostPublished: %s", event["body"]["PostPublished"])
    return respond(None, event)
