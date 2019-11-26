package thumber

import (
	"fmt"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
)

type item struct {
	URL        string
	S3URL      string
	UploadTime int64
}

func prepareDBInput(table, url, s3url string) (*dynamodb.PutItemInput, error) {
	now := time.Now().Unix()
	item := item{
		URL:        url,
		S3URL:      s3url,
		UploadTime: now,
	}
	av, err := dynamodbattribute.MarshalMap(item)
	if err != nil {
		return nil, fmt.Errorf("error marshaling item %v to dynamo: %v", item, err)
	}

	input := &dynamodb.PutItemInput{
		Item:      av,
		TableName: aws.String(table),
	}

	return input, err

}
