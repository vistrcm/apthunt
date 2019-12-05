package main

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/aws/aws-xray-sdk-go/xray"

	"github.com/aws/aws-sdk-go/service/dynamodb"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/go-pkgz/lgr"
	"github.com/vistrcm/apthunt/thumber"
)

//global variables. Yes it is bad in general. This is AWS lambda handler and it is a good practice to have globals
//nolint added because of that.
var (
	t *thumber.Thumber //nolint:gochecknoglobals
	l *lgr.Logger      //nolint:gochecknoglobals
)

//init function required for AWS lambda optimization
func init() { //nolint:gochecknoinits
	//config xray
	err := xray.Configure(xray.Config{LogLevel: "trace"})
	if err != nil {
		panic(fmt.Sprintf("cant' configure xray: %v", err))
	}

	// init Logger, allow debug and caller info, timestamp with milliseconds
	l = lgr.New(lgr.Msec, lgr.Debug, lgr.CallerFile, lgr.CallerFunc)

	// create http http client
	httpClient := &http.Client{Timeout: 1 * time.Minute}

	//S3 manager
	sess := session.Must(session.NewSession())
	// Create an uploader with the session and default options
	uploader := s3manager.NewUploader(sess)
	// create dynamoDB client
	dynamo := dynamodb.New(sess)
	xray.AWS(dynamo.Client)

	// initialize thumber
	t = thumber.NewThumber(uploader, dynamo,
		thumber.WithLogger(l),
		thumber.WithHTTPClient(httpClient))
}

func Handler(ctx context.Context, input string) {
	records := parseInput(input)

	if err := validateURLs(records); err != nil {
		panic(fmt.Sprintf("URL validation failed: %v", err))
	}

	for _, r := range records {
		err := t.Process(r)
		if err != nil {
			l.Logf("WARN error processing %q: %v", r, err)
		}
	}
}

func main() {
	lambda.Start(Handler)
}
