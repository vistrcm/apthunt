package lambda

import (
	"reflect"
	"testing"
)

func Test_parseInput(t *testing.T) {
	type args struct {
		input string
	}
	tests := []struct {
		name string
		args args
		want []string
	}{
		{
			name: "singleURL",
			args: args{input: "http://hello.world"},
			want: []string{"http://hello.world"},
		},
		{
			name: "listURLS",
			args: args{input: "[\"http://hello.world\",\"http://example.com\",\"http://golang.org\"]"},
			want: []string{"http://hello.world", "http://example.com", "http://golang.org"},
		},
		{
			name: "malformedLeft",
			args: args{input: "\"http://hello.world\",\"http://example.com\",\"http://golang.org\"]"},
			want: []string{"\"http://hello.world\",\"http://example.com\",\"http://golang.org\"]"},
		},
		{
			name: "malformedRight",
			args: args{input: "[\"http://hello.world\",\"http://example.com\",\"http://golang.org\""},
			want: []string{"[\"http://hello.world\",\"http://example.com\",\"http://golang.org\""},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := parseInput(tt.args.input); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("parseInput() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_validateURLs(t *testing.T) {
	type args struct {
		records []string
	}
	tests := []struct {
		name    string
		args    args
		wantErr bool
	}{
		{
			name:    "all valid",
			args:    args{[]string{"http://ya.ru", "http://example.com", "http://v.moc"}},
			wantErr: false,
		},
		{
			name:    "all invalid",
			args:    args{[]string{"://ya.ru", "http:example.com", "v.moc"}},
			wantErr: true,
		},
		{
			name:    "some valid",
			args:    args{[]string{"http://ya.ru", "example.com", ""}},
			wantErr: true,
		},
		{
			name:    "one valid",
			args:    args{[]string{"http://example.com"}},
			wantErr: false,
		},
		{
			name:    "one invalid",
			args:    args{[]string{".com"}},
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if err := validateURLs(tt.args.records); (err != nil) != tt.wantErr {
				t.Errorf("validateURLs() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}
