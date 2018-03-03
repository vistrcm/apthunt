ACCOUNT_ID :=$(shell aws sts get-caller-identity --query 'Account' --output text)
ECECUTION_ROLE = "service-role/lambdarole"

vet: *.go
	go vet --all

lint: *.go
	golint *.go

test: vet lint
	go test

build: test
	GOOS=linux go build -o out/lambda_handler lambda_handler.go

zip: build
	cd out && zip handler.zip lambda_handler

out/handler.zip: zip

create-function: out/handler.zip
	aws lambda create-function \
  		--region us-west-1 \
  		--function-name apthunt \
  		--memory 128 \
  		--role arn:aws:iam::$(ACCOUNT_ID):role/$(ECECUTION_ROLE) \
  		--runtime go1.x \
  		--zip-file fileb://$(PWD)/out/handler.zip \
  		--handler lambda_handler \
		--tags project=apthunt,testing=true

delete-function:
	aws lambda delete-function \
		--region us-west-1 \
		--function-name apthunt

re-create-function: delete-function create-function

clean:
	rm -rf out
