OUTDIR=out
ACCOUNT_ID :=$(shell aws sts get-caller-identity --query 'Account' --output text)
ECECUTION_ROLE = "lambda-apthuntparser-role"
FUNCTION_NAME = apthuntparser
REGION = us-west-1

# some for testing
TESTDATE= `date +'%y.%m.%d %H:%M:%S'`

all: clean test zip

clean:
	rm -rf $(OUTDIR)

clean-docker-test:
	docker stop dynamodb ; docker rm dynamodb ; docker network rm lambda-local

cleanall: clean delete-function

pycodestyle: handler.py clparser.py
	pipenv run pycodestyle --show-source --show-pep8 --config .pycodestyle handler.py clparser.py

pylint: handler.py clparser.py
	pipenv run pylint handler.py clparser.py

check: pycodestyle pylint

test-sam: check package lxml
	./test-sam.sh

test-py: test.py
	pipenv run python -m unittest discover -v

test: check test-py test-sam

package: out_dir handler.py clparser.py
	mkdir -p $(OUTDIR)/package && \
	pipenv lock -r > $(OUTDIR)/requirements_tmp.txt && \
	pipenv run pip install --upgrade -t $(OUTDIR)/package -r $(OUTDIR)/requirements_tmp.txt &&\
	cp handler.py clparser.py $(OUTDIR)/package

zip: handler.py clparser.py out_dir package lxml
	cd $(OUTDIR)/package/ && \
	zip -r ../parser.zip *

out_dir:
	mkdir -p $(OUTDIR)

$(OUTDIR)/parser.zip: zip

lxml-clean:
	rm -rf $(OUTDIR)/package/lxml*

# workaround to build lxml
lxml: lxml-clean
	docker run -t -v ${PWD}/out/package:/out/ -v ${PWD}/buildlxml_entry.sh:/buildlxml_entry.sh --entrypoint /buildlxml_entry.sh -u root lambci/lambda:python3.6

create-function: $(OUTDIR)/parser.zip
	aws lambda create-function \
  		--region $(REGION) \
  		--function-name $(FUNCTION_NAME) \
  		--memory 128 \
  		--role arn:aws:iam::$(ACCOUNT_ID):role/$(ECECUTION_ROLE) \
  		--runtime python3.6 \
  		--zip-file fileb://$(PWD)/$(OUTDIR)/parser.zip \
		--handler handler.handler \
		--tags project=apthunt,testing=true

update-function-code: $(OUTDIR)/parser.zip
	aws lambda update-function-code \
		--function-name $(FUNCTION_NAME) \
		--zip-file fileb://$(PWD)/$(OUTDIR)/parser.zip

delete-function:
	aws lambda delete-function \
		--region $(REGION) \
		--function-name $(FUNCTION_NAME)

invoke_get:
	aws lambda  invoke \
		--invocation-type Event \
		--function-name $(FUNCTION_NAME) \
		--region $(REGION) \
		--payload fileb://$(PWD)/testevents/get_event.json \
		output_get.txt

invoke_post:
	aws lambda  invoke \
		--invocation-type Event \
		--function-name $(FUNCTION_NAME) \
		--region $(REGION) \
		--payload fileb://$(PWD)/testevents/post_event.json \
		output_post.txt

test_curl:
	curl -v -X POST -d "wowowowo: $(TESTDATE)" https://fjo9r88qg0.execute-api.us-west-1.amazonaws.com/prod/apthuntparser

.PHONY: deploy
deploy: clean test zip
	cd ../terraform && terraform apply
