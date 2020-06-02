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
        "PostUrl": link,
    }

    print("sending to parser {}: {}. Data: '{}'".format(parser_url, link, data))

    resp = requests.post(parser_url, json=data)
    resp.raise_for_status()
    requestID = resp.json().get("ResponseMetadata", {"RequestId": "NORESP"}).get("RequestId", "NOREQID")
    print(f"RequestId: {requestID}")


def safe_send_to_parser(parser_url, link, retries=5):
    """tries to send_to_parser safely.

    try to send request `retries` times. If failing, pass"""

    for _ in range(retries):
        try:
            send_to_parser(parser_url, link)
        except Exception as ex:
            print("got exception sending link '{}' to parser '{}': '{}'. Retrying.".format(link, parser_url, ex))
        else:
            break
    else:
        print("failed to send link '{}' to parser '{}' {} times.".format(link, parser_url, retries))


def repeat(fn, interval):
    """repeat `fn` every `interval` seconds"""
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


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("search_url", help="url to search links for")
    parser.add_argument("parser_url", help="url to parser service")
    parser.add_argument("--repeat", type=str2bool, nargs='?', const=True, default=True,
                        help="repeat search every 'interval' seconds")
    parser.add_argument("--interval", help="interval to parse", type=int, default=60*60)  # search once an hour 
    return parser.parse_args()


def main():
    args = parse_args()
    if args.repeat:
        repeat(lambda: iteration(args.search_url, args.parser_url), args.interval)
    else:
        iteration(args.search_url, args.parser_url)


if __name__ == "__main__":
    main()
