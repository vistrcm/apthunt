package thumber

import (
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"net/http"

	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/go-pkgz/lgr"
)

type Option func(t *Thumber)

//WithHTTPClient sets thumber's http client
func WithHTTPClient(client *http.Client) Option {
	return func(t *Thumber) {
		t.httpClient = client
	}
}

//WithLogger sets thumber's logger
func WithLogger(l *lgr.Logger) Option {
	return func(t *Thumber) {
		t.l = l
	}
}

//Thumber object can download thumbs from the internet and save in to S3
type Thumber struct {
	uploader   *s3manager.Uploader
	dynamo     *dynamodb.DynamoDB
	l          *lgr.Logger
	httpClient *http.Client
	cache      *Set
}

//Process an URL. Download if needed and store the result in to S3
func (t *Thumber) Process(url string) error {
	if !t.exists(url) {
		return nil // no need to download. Already exists
	}

	reader := t.getReader(url)
	t.upload(reader)

	t.markExists(url)

	return nil
}

//exists check for URL existence in records.
//first check local cache then DynamoDB table.
func (t *Thumber) exists(url string) bool {
	if t.existLocally(url) {
		return true
	}

	if existsInDynamo(url) {
		return true
	}

	return false
}

func existsInDynamo(s string) bool {
	panic("NOT IMPLEMENTED")
}

func (t *Thumber) existLocally(s string) bool {
	return t.cache.Contains(s)
}

//getReader returns Reader of http resource
func (t *Thumber) getReader(s string) interface{} {
	panic("NOT IMPLEMENTED")
}

//upload uploads data from reader to the S3
func (t *Thumber) upload(reader interface{}) {
	panic("NOT IMPLEMENTED")
}

//markExists mark url as exists in the DynamoDB table and local cache
func (t *Thumber) markExists(url string) {
	panic("NOT IMPLEMENTED")
}

//New creates new Thumber
//No real need for API to be extensible via functional options, but implemented to play with
func NewThumber(uploader *s3manager.Uploader, dynamoClient *dynamodb.DynamoDB, opts ...Option) *Thumber {
	// default thumber
	t := Thumber{
		uploader: uploader,
		dynamo: dynamoClient,
		httpClient: http.DefaultClient,
		l:          lgr.New(lgr.Msec),
		cache:      NewSet(),
	}

	// apply options
	for _, opt := range opts {
		opt(&t)
	}

	return &t
}
