.PHONY: fmt
fmt:
	go fmt ./...

.PHONY: test
test:
	AWS_REGION=us-west-1 go test ./...

.PHONY: lint
lint:
	golangci-lint run --enable-all --tests=false
