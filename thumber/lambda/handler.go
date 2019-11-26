package lambda

import (
	"fmt"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/go-pkgz/lgr"
	"github.com/vistrcm/apthunt/thumber"
	"net/http"
	"time"
)

//global variables. Yes it is bad in general. This is AWS lambda handler and it is a good practice to have globals
//nolint added because of that.
var (
	t *thumber.Thumber //nolint:gochecknoglobals
	l *lgr.Logger      //nolint:gochecknoglobals
)

func init() { //nolint:gochecknoinits this is AWS lambda. Need init function.
	// init Logger, allow debug and caller info, timestamp with milliseconds
	l = lgr.New(lgr.Msec, lgr.Debug, lgr.CallerFile, lgr.CallerFunc)

	// create http http client
	httpClient := &http.Client{Timeout: 1 * time.Minute}

	//S3 manager
	sess := session.Must(session.NewSession())
	// Create an uploader with the session and default options
	uploader := s3manager.NewUploader(sess)

	// initialize thumber
	t = thumber.NewThumber(
		thumber.WithLogger(l),
		thumber.WithHTTPClient(httpClient),
		thumber.WithUploader(uploader))
}

func Handler(input string) {
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
