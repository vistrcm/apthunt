.DEFAULT_GOAL := precommit

.PHONY: precommit
precommit: fmt test lint

.PHONY: fmt
fmt:
	go fmt ./... && goimports -w .

.PHONY: test
test:
	go test ./...

.PHONY: lint
lint:
	golangci-lint run --enable-all --tests=false

.PHONY: build_handler
build_handler: precommit out/handler

out/handler: cmd/lambda/handler.go processor.go
	GOOS=linux go build -o out/handler cmd/lambda/handler.go

.PHONY: clean
clean:
	rm -rf out/*

.PHONY: deploy
deploy: build_handler
	cd ../terraform && terraform apply
