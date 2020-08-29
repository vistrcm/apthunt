package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/vistrcm/apthunt/processor"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-xray-sdk-go/xray"
	"github.com/go-pkgz/lgr"
)

//global variables. Yes it is bad in general. This is AWS lambda handler and it is a good practice to have globals
//nolint added because of that.
var (
	l          *lgr.Logger  //nolint:gochecknoglobals
	httpClient *http.Client //nolint:gochecknoglobals
)

// httpTimeout timeout for http calls in seconds.
const httpTimeout = 10

// init function required for AWS lambda optimization.
func init() { //nolint:gochecknoinits
	// config xray
	err := xray.Configure(xray.Config{LogLevel: "info"})
	if err != nil {
		panic(fmt.Sprintf("cant' configure xray: %v", err))
	}

	// init Logger, allow debug and caller info, timestamp with milliseconds
	l = lgr.New(lgr.Msec, lgr.Debug, lgr.CallerFile, lgr.CallerFunc)

	httpClient = &http.Client{
		Timeout: time.Second * httpTimeout,
	}
}

// Handler handler function for AWS Lambda.
func Handler(ctx context.Context, sqsEvent events.SQSEvent) error {
	// Start a subsegment
	ctx, seg := xray.BeginSubsegment(ctx, "processor")
	defer seg.Close(nil)

	log.Printf("handler with context: %+v", ctx)

	proc := processor.NewProcessor(processor.WithLogger(l), processor.WithHTTPClient(httpClient))

	for _, message := range sqsEvent.Records {
		log.Printf("The message %s for event source %s = %s\n",
			message.MessageId, message.EventSource, message.Body)

		err := proc.ProcessMessage(message.Body)
		if err != nil {
			return err
		}
	}

	return nil
}

func main() {
	lambda.Start(Handler)
}
