package main

import (
	"context"
	"fmt"

	"github.com/aws/aws-lambda-go/lambdacontext"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-xray-sdk-go/xray"
)

type myEvent struct {
	Name string `json:"name"`
}

//MyResponse structure of response
type MyResponse struct {
	Message string `json:"message"`
}

// HandleRequest of some kind
func HandleRequest(ctx context.Context, name myEvent) (MyResponse, error) {
	xray.Configure(xray.Config{
		LogLevel:       "info", // default
		ServiceVersion: "1.2.3",
	})

	lc, _ := lambdacontext.FromContext(ctx)
	log.print(lc.Identity.CognitoIdentityPoolID)

	return MyResponse{Message: fmt.Sprintf("Who are you, %s?", name.Name)}, nil
}

func main() {
	lambda.Start(HandleRequest)
}
