package thumber

import (
	"context"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"

	"github.com/aws/aws-sdk-go/aws"

	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/go-pkgz/lgr"
)

type Option func(t *Thumber)

//ErrKeyMismatch indicates that key exist in the Dynamo, but value does not match.
var ErrKeyMismatch = errors.New("key mismatch")

//ErrGetReq indicates failure of getting url.
var ErrGetReq = errors.New("fail to GET url")

//WithHTTPClient sets thumber's http client.
func WithHTTPClient(client *http.Client) Option {
	return func(t *Thumber) {
		t.httpClient = client
	}
}

//WithLogger sets thumber's logger.
func WithLogger(l *lgr.Logger) Option {
	return func(t *Thumber) {
		t.l = l
	}
}

//WithDynamoTableName sets DynamoDB name to store thumb meta.
func WithDynamoTableName(table string) Option {
	return func(t *Thumber) {
		t.tableName = table
	}
}

//Thumber object can download thumbs from the internet and save in to S3.
type Thumber struct {
	uploader   *s3manager.Uploader
	bucket     string
	dynamo     *dynamodb.DynamoDB
	tableName  string
	l          *lgr.Logger
	httpClient *http.Client
	cache      *Set
}

//Process an URL. Download if needed and store the result in to S3.
func (t *Thumber) Process(ctx context.Context, url string) error {
	exist, existsErr := t.exists(ctx, url)
	if existsErr != nil {
		return fmt.Errorf("error checking %q for existence: %w", url, existsErr)
	}

	if exist {
		t.l.Logf("entity %q already downloaded", url)
		return nil // no need to download. Already exists
	}

	reader, err := t.getReader(url)
	if err != nil {
		t.l.Logf("WARN error getting reader for %q: %v", url, err)
		return fmt.Errorf("error getting reader for %q. %w", url, err)
	}

	key, err := getKeyForURL(url)
	if err != nil {
		t.l.Logf("WARN can not get key for the url %q: %v", url, err)
		return fmt.Errorf("can not get key for the url %q: %w", url, err)
	}

	s3url, err := t.upload(key, reader)
	if err != nil {
		t.l.Logf("WARN can't upload %q to s3: %v", url, err)
		return fmt.Errorf("can't upload %q. %w", url, err)
	}

	err = t.markExists(ctx, url, s3url)

	return err
}

func getKeyForURL(u string) (string, error) {
	parsed, err := url.ParseRequestURI(u)
	if err != nil {
		return "", err
	}

	return parsed.Path, nil
}

//exists check for URL existence in records.
//first check local cache then DynamoDB table.
func (t *Thumber) exists(ctx context.Context, url string) (bool, error) {
	if t.existLocally(url) {
		return true, nil
	}

	inDynamo, err := t.existsInDynamo(ctx, url)
	if err != nil {
		return false, err
	}

	return inDynamo, nil
}

func (t *Thumber) existsInDynamo(ctx context.Context, url string) (bool, error) {
	input := &dynamodb.GetItemInput{
		TableName: aws.String(t.tableName),
		Key: map[string]*dynamodb.AttributeValue{
			"URL": {
				S: aws.String(url),
			},
		},
	}

	//specify attribute to get
	attributeToGet := aws.String("URL")
	input = input.SetAttributesToGet([]*string{attributeToGet})
	result, err := t.dynamo.GetItemWithContext(ctx, input)

	if err != nil {
		return false, err
	}

	retrieved, ok := result.Item["URL"]

	if !ok { // not found in dynamo
		return false, nil
	}

	//small additional check
	if url != *retrieved.S {
		return false, fmt.Errorf("found item in dynamo, but key is different.: "+
			"%q != %q. %w", url, retrieved, ErrKeyMismatch)
	}

	// all looks ok
	return true, nil
}

func (t *Thumber) existLocally(s string) bool {
	return t.cache.Contains(s)
}

//getReader returns Reader of http resource.
func (t *Thumber) getReader(url string) (io.ReadCloser, error) {
	// response body will be closed later on stack. See upload().
	resp, err := t.httpClient.Get(url) //nolint:bodyclose

	if err != nil {
		t.l.Logf("WARN error getting %q", url)
		return nil, fmt.Errorf("error getting %q, %w", url, ErrGetReq)
	}

	return resp.Body, nil
}

//upload uploads data from reader to the S3.
func (t *Thumber) upload(key string, reader io.ReadCloser) (string, error) {
	//need to close reader at the end
	defer func() {
		if err := reader.Close(); err != nil {
			panic(fmt.Sprintf("can't close reader: %v", err))
		}
	}()

	out, err := t.uploader.Upload(&s3manager.UploadInput{
		Bucket: &t.bucket,
		Key:    &key,
		Body:   reader,
	})

	if err != nil {
		t.l.Logf("WARN Unable to upload %q to %q, %v", key, t.bucket, err)
		return "", fmt.Errorf("unable to upload to s3: %w", err)
	}

	return out.Location, nil
}

//markExists mark url as exists in the DynamoDB table and local cache.
func (t *Thumber) markExists(ctx context.Context, url, s3url string) error {
	input, err := prepareDBInput(t.tableName, url, s3url)
	if err != nil {
		return fmt.Errorf("error preparing item: %w", err)
	}

	_, err = t.dynamo.PutItemWithContext(ctx, input)
	if err != nil {
		return fmt.Errorf("error calling PutItem on %v: %w", input, err)
	}

	return nil
}

//New creates new Thumber
//No real need for API to be extensible via functional options, but implemented to play with.
func NewThumber(uploader *s3manager.Uploader, dynamoClient *dynamodb.DynamoDB, opts ...Option) *Thumber {
	//build http client with defined timeout
	const httpTimeout = 30

	var httpClient = &http.Client{
		Timeout: httpTimeout * time.Second,
	}

	// default thumber
	t := Thumber{
		uploader:   uploader,
		bucket:     "apthunt.thumbs",
		dynamo:     dynamoClient,
		tableName:  "thumbs",
		httpClient: httpClient,
		l:          lgr.New(lgr.Msec),
		cache:      NewSet(),
	}

	// apply options
	for _, opt := range opts {
		opt(&t)
	}

	return &t
}
