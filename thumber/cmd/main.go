package main

import (
	"fmt"
	"net/http"
	"time"

	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/go-pkgz/lgr"
	"github.com/vistrcm/apthunt/thumber"
)

//yes, global variables. This is best practice for the AWS Lambda.

func main() {
	// init Logger, allow debug and caller info, timestamp with milliseconds
	l := lgr.New(lgr.Msec, lgr.Debug, lgr.CallerFile, lgr.CallerFunc)

	// create http http client
	httpClient := &http.Client{Timeout: 1 * time.Minute}

	//S3 manager
	sess := session.Must(session.NewSession())
	// Create an uploader with the session and default options
	uploader := s3manager.NewUploader(sess)
	// create dynamoDB client
	dynamo := dynamodb.New(sess)

	// initialize thumber
	t := thumber.NewThumber(uploader, dynamo,
		thumber.WithLogger(l),
		thumber.WithHTTPClient(httpClient))

	err := t.Process("https://images.craigslist.org/00d0d_fG6ynpO9XAM_600x450.jpg")
	fmt.Printf("err: %v\n", err)
}
