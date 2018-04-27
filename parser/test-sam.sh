#!/bin/bash

set -x
set -v 
set -e

# test posting empty body
sam local invoke ApthuntParser --event testevents/post_empty_event.json | egrep "errorMessage.*stackTrace" && exit 1

# test posting some body
sam local invoke ApthuntParser --event testevents/post_event.json | egrep "errorMessage.*stackTrace" && exit 1


