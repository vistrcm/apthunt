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
