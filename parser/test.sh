#!/bin/bash
set -x
set -v
set -e


for link in `cat testlinks`
do
        pipenv run python clparser.py ${link}
done

