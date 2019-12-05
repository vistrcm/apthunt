package thumber

import "testing"

func Test_getKeyForURL(t *testing.T) {
	type args struct {
		u string
	}
	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		{
			name:    "num",
			args:    args{"http://a.com/1234"},
			want:    "/1234",
			wantErr: false,
		},
		{
			name:    "complex",
			args:    args{"http://a.com/1/2/3/4"},
			want:    "/1/2/3/4",
			wantErr: false,
		},
		{
			name:    "empty",
			args:    args{""},
			want:    "",
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := getKeyForURL(tt.args.u)
			if (err != nil) != tt.wantErr {
				t.Errorf("getKeyForURL(%q) error = %v, wantErr %v. Err: %v", tt.args.u, err, tt.wantErr, err)
				return
			}
			if got != tt.want {
				t.Errorf("getKeyForURL(%q) got = %v, want %v", tt.args.u, got, tt.want)
			}
		})
	}
}
