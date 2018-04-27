#!/bin/bash

set -x
set -v 
set -e

# test posting empty body
sam local invoke ApthuntParser --event testevents/post_empty_event.json | egrep "errorMessage.*stackTrace" && exit 1

# test posting some body
sam local invoke ApthuntParser --event testevents/post_event.json | egrep "errorMessage.*stackTrace" && exit 1

echo "looks like sam tests are ok"  # need this to not exit with 1 in case of normal execution
