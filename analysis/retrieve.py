import concurrent
import os
import pickle
import sys
from concurrent.futures.process import ProcessPoolExecutor

import boto3
from boto3.dynamodb import types


def dynamo2python(deserializer, items):
    python_data = [
        {k: deserializer.deserialize(v) for k, v in it.items()}
        for it in items
    ]
    return python_data


def data_retrieve(table, segment=0, total_segments=1, page_size=1000):
    """download data from table"""
    client = boto3.client('dynamodb')
    paginator = client.get_paginator('scan')
    deserializer = types.TypeDeserializer()

    counter = 0
    items = []
    for page in paginator.paginate(TableName=table,
                                   TotalSegments=total_segments,
                                   Segment=segment,
                                   PaginationConfig={
                                       "PageSize": page_size,
                                   }):

        deserealized = dynamo2python(deserializer, page["Items"])
        items.extend(deserealized)

        counter += 1
        if counter % 100 == 0:
            print(f"s{segment}. pages: {counter}, items {len(items)}. size {sys.getsizeof(items)}")

    return items


def parallel_data_retrieve(table, max_workers=4):
    segments = [i for i in range(max_workers)]
    items = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # start the load operation and mark each future with segment number
        future_to_segment = {
            executor.submit(data_retrieve, table, segment=sgmt, total_segments=max_workers): sgmt
            for sgmt in segments
        }

        for future in concurrent.futures.as_completed(future_to_segment):
            segment = future_to_segment[future]
            try:
                print(f"segment {segment}/{max_workers} completed")
                records = future.result()
                items.extend(records)
            except Exception as exc:
                fexc = future.exception()
                print('%r generated an exception: %s. %s' % (segment, exc, fexc))

    return items


def maybe_pickle(records, filename, force=False):
    if os.path.exists(filename) and not force:
        # You may override by setting force=True.
        print('%s already present - Skipping pickling.' % filename)
    else:
        print('Pickling %s.' % filename)
        try:
            with open(filename, 'wb') as f:
                pickle.dump(records, f, pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print('Unable to save data to', filename, ':', e)


def maybe_download(table, force=False):
    storage_file = table + ".pkl"
    if force or not os.path.exists(storage_file):
        # records = data_retrieve(table)
        records = parallel_data_retrieve(table)
        maybe_pickle(records, storage_file, force)
    return storage_file


if __name__ == "__main__":
    data_file = maybe_download("apthunt", force=True)
    print("loading back")
    data = pickle.load(open(data_file, 'rb'))
    print(len(data))
