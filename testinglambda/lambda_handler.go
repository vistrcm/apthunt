package main

import (
	"context"
	"fmt"
	"log"

	"github.com/aws/aws-lambda-go/lambda"
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
	log.Println("wowowowo function")
	return MyResponse{Message: fmt.Sprintf("Who are you, %s?", name.Name)}, nil

}

func main() {
	lambda.Start(HandleRequest)
}
