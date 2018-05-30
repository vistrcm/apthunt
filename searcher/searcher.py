#!/usr/bin/env python
import argparse
import time
from collections import defaultdict

import requests
from requests_html import HTMLSession

PROCESSED = defaultdict(int)

def search(url):
    """search for classifieds in url. Returns list of URLs"""
    print("searching in {}".format(url))
    session = HTMLSession()
    r = session.get(url)
    rows = r.html.find('.rows', first=True)
    return rows.absolute_links


def send_to_parser(parser_url, link):
    """send link to parser url in specific format"""

    data = {
        "FeedTitle": "simulated",
        "FeedUrl": "simulated",
        "PostTitle": "simulated",
        "PostUrl": link,
        "PostContent": "simulated",
        "PostPublished": "simulated"
    }

    print("sending to parser {}: {}. Data: '{}'".format(parser_url, link, data))

    resp = requests.post(parser_url, json=data)
    resp.raise_for_status()
    print(resp.json())


def safe_send_to_parser(parser_url, link):
    try:
        send_to_parser(parser_url, link)
    except Exception as ex:
        print("got exception sending link '{}' to parser '{}': '{}'".format(parser_url, link, ex))


def repeat(fn, interval):
    "repeat `fn` every `interval` seconds"
    brk = False
    while not brk:
        start = time.monotonic()
        fn()
        now = time.monotonic()
        excution_duration = now - start
        sleep_time = interval - excution_duration
        if sleep_time > 0.0:
            print("sleeping for {}".format(sleep_time))
            time.sleep(interval - excution_duration)


def iteration(search_url, parser_url):
    res = search(search_url)
    for link in res:
        if PROCESSED[link] < 1:  # send if not processed yet
            safe_send_to_parser(parser_url, link)
        PROCESSED[link] += 1


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("search_url", help="url to search links for")
    parser.add_argument("parser_url", help="url to parser service")
    parser.add_argument("--interval", help="interval to parse", type=int, default=60*60)  # search once an hour 
    return parser.parse_args()


def main():
    args = parse_args()
    repeat(lambda : iteration(args.search_url, args.parser_url), args.interval)


if __name__ == "__main__":
    main()
