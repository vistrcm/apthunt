package processor

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"math"
	"net/http"
	"os"

	"github.com/go-pkgz/lgr"
)

const (
	threshold = 500
)

type record struct {
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
	District  string  `json:"district"`
	Housing   string  `json:"housing"`
	Bedrooms  float64 `json:"bedrooms"`
	Area      float64 `json:"area"`
	Type      string  `json:"type"`
	CatsOK    bool    `json:"catsok"`
	DogsOK    bool    `json:"dogsok"`
	GarageA   bool    `json:"garagea"`
	GarageD   bool    `json:"garaged"`
	Furnished bool    `json:"furnished"`
	LaundryB  bool    `json:"laundryb"`
	LaundryS  bool    `json:"laundrys"`
	WD        bool    `json:"wd"`
	NThumbs   int     `json:"nthumbs"`
}

type extendedRecord struct {
	record
	Price float64 `json:"price"`
	URL   string  `json:"url"`
}

type botResponse struct {
	Ok bool `json:"ok"`
}

//ErrBadBotResponse indicates failure of getting url.
var ErrBadBotResponse = errors.New("bad bot response")

//ErrNoRequiredEnvVar indicates absence of required environment variable.
var ErrNoRequiredEnvVar = errors.New("no required environment variable")

func getExtRecord(data []byte) (extendedRecord, error) {
	var rec extendedRecord

	if err := json.Unmarshal(data, &rec); err != nil {
		return extendedRecord{}, fmt.Errorf("error unmarshaling %q: %w", data, err)
	}

	return rec, nil
}

func getExtRecords(data []byte) ([]extendedRecord, error) {
	var rec []extendedRecord

	if err := json.Unmarshal(data, &rec); err != nil {
		return []extendedRecord{}, fmt.Errorf("error unmarshaling %q: %w", data, err)
	}

	return rec, nil
}

//Processor message processor: parse message, predict price and send message if difference is bigger than Threshold.
type Processor struct {
	l          *lgr.Logger
	threshold  int
	httpClient *http.Client
}

//WithLogger optional function to set logger.
func WithLogger(l *lgr.Logger) func(*Processor) {
	return func(processor *Processor) {
		processor.l = l
	}
}

//WithThreshold optional function to set threshold for the processor.
func WithThreshold(t int) func(*Processor) {
	return func(processor *Processor) {
		processor.threshold = t
	}
}

//WithHTTPClient set http client for the processor.
func WithHTTPClient(c *http.Client) func(*Processor) {
	return func(processor *Processor) {
		processor.httpClient = c
	}
}

//NewProcessor builds new processor.
func NewProcessor(options ...func(*Processor)) Processor {
	proc := Processor{threshold: threshold}

	for _, option := range options {
		option(&proc)
	}

	return proc
}

func (p *Processor) ProcessMessage(data string) error {
	extRec, err := getExtRecord([]byte(data))
	if err != nil {
		return fmt.Errorf("error getting record: %w", err)
	}

	predictions, err := p.predict(extRec.record)
	if err != nil {
		return fmt.Errorf("error during prediction: %w", err)
	}

	for _, prediction := range predictions {
		p.l.Logf("INFO url: %q. prediction: %f. price: %f", extRec.URL, prediction.Price, extRec.Price)

		if math.Abs(prediction.Price-extRec.Price) > threshold {
			p.l.Logf("INFO interesting result")

			err := p.message(extRec, prediction.Price)
			if err != nil {
				return fmt.Errorf("error sending message: %w", err)
			}
		}
	}

	return nil
}

func (p *Processor) predict(r record) ([]extendedRecord, error) {
	predictorURL, err := getPredictorURL()
	if err != nil {
		return nil, err
	}

	var listRec = []record{r} // list of records from single record. Required for predictor

	jsonStr, err := json.Marshal(listRec)
	if err != nil {
		return nil, fmt.Errorf("can't marshal. %w", err)
	}

	if err != nil {
		return nil, fmt.Errorf("error converting record to bytes: %w", err)
	}

	p.l.Logf("INFO request to predictor: %q", jsonStr)

	req, err := http.NewRequest("POST", predictorURL, bytes.NewBuffer(jsonStr))
	if err != nil {
		return nil, fmt.Errorf("error creating request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := p.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error on http request: %w", err)
	}

	defer func() {
		err := resp.Body.Close()
		if err != nil {
			p.l.Logf("WARN. Can't close the response body: %+v", err)
		}
	}()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %w", err)
	}

	rec, err := getExtRecords(body)
	if err != nil {
		return nil, fmt.Errorf("error parsing response: %w", err)
	}

	return rec, nil
}

func (p *Processor) message(rec extendedRecord, prediction float64) error {
	botURL, err := getBotURL()
	if err != nil {
		return err
	}

	userID, err := getUserID()
	if err != nil {
		return err
	}

	p.l.Logf("INFO sending message to the user: %q", userID)

	payload := struct {
		ChatID string `json:"chat_id"`
		Text   string `json:"text"`
	}{
		ChatID: userID,
		Text:   fmt.Sprintf("%q looks interesting. Price: %f. Prediction: %f", rec.URL, rec.Price, prediction),
	}

	var jsonStr, marshalErr = json.Marshal(payload)
	if marshalErr != nil {
		return fmt.Errorf("error converting payload %+v to bytes: %w", payload, err)
	}

	req, err := http.NewRequest("POST", botURL, bytes.NewBuffer(jsonStr))
	if err != nil {
		return fmt.Errorf("error creating request to bot: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := p.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("error on http request: %w", err)
	}

	defer func() {
		err := resp.Body.Close()
		if err != nil {
			p.l.Logf("WARN. Can't close the response body: %+v", err)
		}
	}()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("error reading bot response body: %w", err)
	}

	var botResp botResponse

	if err := json.Unmarshal(body, &botResp); err != nil {
		return fmt.Errorf("error unmarshaling bot response %q: %w", body, err)
	}

	if !botResp.Ok {
		return fmt.Errorf("bot response is not ok %q, %w", body, ErrBadBotResponse)
	}

	return nil
}

func getUserID() (string, error) {
	id, ok := os.LookupEnv("USER_ID")
	if !ok {
		return "", fmt.Errorf("USER_ID is not set. %w", ErrNoRequiredEnvVar)
	}

	return id, nil
}

func getBotURL() (string, error) {
	url, ok := os.LookupEnv("BOT_URL")
	if !ok {
		return "", fmt.Errorf("BOT_URL is not set. %w", ErrNoRequiredEnvVar)
	}

	return url, nil
}

func getPredictorURL() (string, error) {
	url, ok := os.LookupEnv("PREDICTOR_URL")
	if !ok {
		return "", fmt.Errorf("PREDICTOR_URL is not set. %w", ErrNoRequiredEnvVar)
	}

	return url, nil
}
