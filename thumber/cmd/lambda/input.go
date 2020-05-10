package main

import (
	"encoding/json"
	"fmt"
	"net/url"
)

func parseInput(input string) []string {
	// try to load as json array
	var records []string
	err := json.Unmarshal([]byte(input), &records)

	if err != nil { // looks like input is not an JSON array
		// assume it is single URL
		records = []string{input}
	}

	return records
}

func validateURLs(records []string) error {
	var errs []error

	for _, record := range records {
		_, err := url.ParseRequestURI(record)
		if err != nil {
			errs = append(errs, err)
		}
	}

	if len(errs) > 0 { // errors found
		return fmt.Errorf("found mailformed urls: %+v", errs) //nolint:goerr113 // return list of errors here
	}

	return nil
}
