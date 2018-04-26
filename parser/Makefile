OUTDIR=out
ACCOUNT_ID :=$(shell aws sts get-caller-identity --query 'Account' --output text)
ECECUTION_ROLE = "lambda-apthuntparser-role"
FUNCTION_NAME = apthuntparser
REGION = us-west-1

# some for testing
TESTDATE= `date +'%y.%m.%d %H:%M:%S'`

all: zip

clean:
	rm -rf $(OUTDIR)

cleanall: clean delete-function

zip: parser.py out_dir
	zip $(OUTDIR)/parser.zip parser.py

out_dir:
	mkdir -p $(OUTDIR)

$(OUTDIR)/parser.zip: zip

create-function: $(OUTDIR)/parser.zip
	aws lambda create-function \
  		--region $(REGION) \
  		--function-name $(FUNCTION_NAME) \
  		--memory 128 \
  		--role arn:aws:iam::$(ACCOUNT_ID):role/$(ECECUTION_ROLE) \
  		--runtime python3.6 \
  		--zip-file fileb://$(PWD)/$(OUTDIR)/parser.zip \
  		--handler parser.handler \
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
