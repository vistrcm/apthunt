import concurrent
import re
from collections import Counter
from concurrent import futures
from decimal import Decimal

import boto3

SAVED_NULL = {"NULL": True}


def get_bedrooms(housing):
    """parse amount of bedrooms from 'housing' field"""
    bedrooms = None
    # bedrooms
    match = re.search(r'(\d+)br.*', housing)
    if match:
        bedrooms = float(match.group(1))
    return bedrooms


def data_retrieve(table, page_size=100):
    """download data from table"""
    client = boto3.client('dynamodb')
    paginator = client.get_paginator('scan')

    for page in paginator.paginate(
            TableName=table,
            PaginationConfig={"PageSize": page_size},
            AttributesToGet=[
                'intid',
                'parsed_housing',
                'parsed_bedrooms',
            ],
    ):
        for item in page["Items"]:
            yield item


def update_item(table_name, item, fixed_bedrooms):
    table = boto3.resource('dynamodb').Table(table_name)

    intid = item["intid"]["S"]

    response = table.update_item(
        Key={
            'intid': intid,
        },
        UpdateExpression="set parsed_bedrooms = :h",
        ExpressionAttributeValues={
            ':h': fixed_bedrooms,
        },
        ReturnValues="UPDATED_NEW"
    )

    return response


def print_count(counter):
    count = len(list(counter.elements()))

    if count % 111 != 0:
        return

    print(f"total items {count}")
    for k, v in counter.items():
        print(f"{k}: {v}")

    print()


def process_item(table_name, item, counter):
    if item.get("parsed_housing") is None:
        counter.update(["no_housing"])
        print_count(counter)
        return

    if item["parsed_housing"] == SAVED_NULL:
        counter.update(["saved_null_housing"])
        print_count(counter)
        return

    housing = item["parsed_housing"]["S"]
    fixed_bedrooms = get_bedrooms(housing)

    if fixed_bedrooms is None:
        counter.update(["missed_info"])
        print_count(counter)
        return

    fixed_bedrooms = Decimal(fixed_bedrooms)
    if item.get("parsed_bedrooms") is None:
        _ = update_item(table_name, item, fixed_bedrooms)
        counter.update(["no_parsed"])
        print_count(counter)
        return

    if item["parsed_bedrooms"] == SAVED_NULL:
        _ = update_item(table_name, item, fixed_bedrooms)
        counter.update(["saved_null_bedrooms"])
        print_count(counter)
        return

    saved_bedrooms = Decimal(item["parsed_bedrooms"]["N"])
    if saved_bedrooms != fixed_bedrooms:
        _ = update_item(table_name, item, fixed_bedrooms)
        counter.update(["wrong_bedrooms"])
        print_count(counter)
        return

    counter.update(["skipped"])
    print_count(counter)


def main():
    table_name = "apthunt"
    counter = Counter()

    # for item in data_retrieve(table_name):
    #     process_item(table_name, item, counter)

    # We can use a with statement to ensure threads are cleaned up promptly
    with futures.ThreadPoolExecutor(max_workers=6) as executor:
        # Start the load operations and mark each future with its item
        future_to_item = {executor.submit(process_item, table_name, item, counter): item for item in
                          data_retrieve(table_name)}
        completed = 0
        for future in concurrent.futures.as_completed(future_to_item):
            completed += 1
            print(f"completed: {completed}")

            item = future_to_item[future]
            try:
                _ = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (item, exc))


if __name__ == "__main__":
    main()
