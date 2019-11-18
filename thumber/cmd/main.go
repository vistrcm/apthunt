package main

import (
	"fmt"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/aws/aws-sdk-go/service/sqs"
	"github.com/go-pkgz/lgr"
	"io"
	"net/http"
	"os"
	"time"
)

//yes, global variables. This is best practice for the AWS Lambda.
var (
	uploader   *s3manager.Uploader
	l          *lgr.Logger
	httpClient *http.Client
	sqsSVC     *sqs.SQS
)

func main() {
	// initialize

	// allow debug and caller info, timestamp with milliseconds
	l = lgr.New(lgr.Msec, lgr.Debug, lgr.CallerFile, lgr.CallerFunc)

	//	aws
	sess := session.Must(session.NewSession())

	// Create an uploader with the session and default options
	uploader = s3manager.NewUploader(sess)

	httpClient = &http.Client{
		Timeout: time.Minute * 1,
	}

	//img := "https://images.craigslist.org/00I0I_1gOqlQZz2O7_600x450.jpg"
	filename := "go.sum"
	myBucket := "apthunt.thumbs"
	myString := filename

	result, err := sqsSVC.GetQueueUrl(&sqs.GetQueueUrlInput{
		QueueName: aws.String("apthunt-thumbs"),
	})

	if err != nil {
		fmt.Println("Error", err)
		return
	}

	fmt.Println("Success", *result.QueueUrl)

	f, err := os.Open(filename)
	if err != nil {
		panic(fmt.Errorf("failed to open file %q, %v", filename, err))
	}

	location, err := uploadFile(myBucket, myString, f)
	if err != nil {
		panic(fmt.Errorf("can't upload: %v", err))
	}
	l.Logf("uploaded to %s", location)
}

//uploadFile uploads file from reader to the bucket under key
//returns result location
func uploadFile(bucket string, key string, reader io.Reader) (string, error) {
	// Upload the file to S3.
	result, err := uploader.Upload(&s3manager.UploadInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
		Body:   reader,
	})
	if err != nil {
		return "", fmt.Errorf("failed to upload file, %v", err)
	}
	return aws.StringValue(&result.Location), nil
}
