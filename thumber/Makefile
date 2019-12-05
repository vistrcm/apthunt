.DEFAULT_GOAL := precommit

.PHONY: precommit
precommit: fmt test lint

.PHONY: fmt
fmt:
	go fmt ./... && goimports -w .

.PHONY: test
test:
	AWS_REGION=us-west-1 go test ./...

.PHONY: lint
lint:
	golangci-lint run --enable-all --tests=false

.PHONY: build_handler
build_handler: precommit handler

handler: cmd/lambda/handler.go cmd/lambda/input.go
	GOOS=linux go build cmd/lambda/handler.go cmd/lambda/input.go

.PHONY: package
package: function.zip

function.zip: build_handler
	zip function.zip handler

.PHONY: update_lambda
update_lambda: package
	docker run -it \
	-e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
	-e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
	-v ${PWD}:/app/ \
	vistrcm/awscli \
	lambda update-function-code --function-name thumber \
	--zip-file fileb://app/function.zip \
	--region ${AWS_REGION}

.PHONY: clean
clean:
	rm function.zip handler
