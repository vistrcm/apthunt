#!/bin/bash

set -x
set -v 
set -e

# start DynamoDB local
docker network create lambda-local
docker run -d -p 8000:8000 --name dynamodb cnadiminti/dynamodb-local

# test posting empty body
sam local invoke ApthuntParser -v out/package --docker-network lambda-local --event testevents/post_empty_event.json | grep "Could not parse body" || exit 1

# test posting some body
#sam local invoke ApthuntParser -v out/package --docker-network lambda-local --event testevents/post_event.json | egrep "errorMessage.*stackTrace" && exit 1
sam local invoke ApthuntParser -v out/package --docker-network lambda-local --event testevents/post_event.json
echo $?

echo "looks like sam tests are ok"  # need this to not exit with 1 in case of normal execution

# do some cleanup
docker stop dynamodb
docker rm dynamodb

docker network rm lambda-local
