package thumber

import (
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/go-pkgz/lgr"
	"net/http"
)

type option func(t *Thumber)

//WithHTTPClient sets thumber's http client
func WithHTTPClient(client *http.Client) option {
	return func(t *Thumber) {
		t.httpClient = client
	}
}

//WithLogger sets thumber's logger
func WithLogger(l *lgr.Logger) option {
	return func(t *Thumber) {
		t.l = l
	}
}

func WithUploader(u *s3manager.Uploader) option {
	return func(t *Thumber) {
		t.uploader = u
	}
}

//Thumber object can download thumbs from the internet and save in to S3
type Thumber struct {
	l          *lgr.Logger
	httpClient *http.Client
	uploader   *s3manager.Uploader
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

//exists check for URL existance in records
func (t *Thumber) exists(url string) bool {
	panic("NOT IMPLEMENTED")
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
func (t *Thumber) markExists(URL string) {
	panic("NOT IMPLEMENTED")
}

//New creates new Thumber
//No real need for API to be extensible via functional options, but implemented to play with
func NewThumber(opts ...option) *Thumber {
	// default thumber
	t := Thumber{
		httpClient: http.DefaultClient,
		l:          lgr.New(lgr.Msec),
	}

	// apply options
	for _, opt := range opts {
		opt(&t)
	}

	return &t
}
