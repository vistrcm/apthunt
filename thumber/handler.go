package thumber

import (
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/go-pkgz/lgr"
	"net/http"
	"time"
)

//global variables. Yes it is bad in general. This is AWS lambda handler and it is a good practice to have globals
var (
	thumber *Thumber
	l       *lgr.Logger
)

func init() {
	// init Logger, allow debug and caller info, timestamp with milliseconds
	l = lgr.New(lgr.Msec, lgr.Debug, lgr.CallerFile, lgr.CallerFunc)

	// create http http client
	httpClient := &http.Client{Timeout: 1 * time.Minute}

	//S3 manager
	sess := session.Must(session.NewSession())
	// Create an uploader with the session and default options
	uploader := s3manager.NewUploader(sess)

	// initialize thumber
	thumber = NewThumber(
		WithLogger(l),
		WithHTTPClient(httpClient),
		WithUploader(uploader))
}

func Handler(input string) {
	records, err := parseInput(input)
	if err != nil {

	}

	for _, r := range records {
		err := thumber.Process(r)
		if err != nil {
			l.Logf("WARN error processing %q: %v", r, err)
		}
	}
}
