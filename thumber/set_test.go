package thumber

import (
	"reflect"
	"testing"
)

func TestNewSet(t *testing.T) {
	tests := []struct {
		name string
		want *set
	}{
		{
			name: "create",
			want: &set{m: make(map[string]void)},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := NewSet(); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("NewSet() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_set_Contains(t *testing.T) {
	type fields struct {
		m map[string]void
	}
	type args struct {
		key string
	}
	tests := []struct {
		name   string
		fields fields
		args   args
		want   bool
	}{
		{
			name: "hit_data",
			fields: fields{m: map[string]void{"foo": struct{}{}, "bar": struct{}{}}},
			args: args{key: "foo"},
			want: true,
		},
		{
			name: "miss_data",
			fields: fields{m: map[string]void{"foo": struct{}{}, "bar": struct{}{}}},
			args: args{key: "baar"},
			want: false,
		},
		{
			name: "hit_no_data",
			fields: fields{m: make(map[string]void)},
			args: args{key: "foo"},
			want: false,
		},
		{
			name: "miss_no_data",
			fields: fields{m: make(map[string]void)},
			args: args{key: "baar"},
			want: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			s := &set{
				m: tt.fields.m,
			}
			if got := s.Contains(tt.args.key); got != tt.want {
				t.Errorf("Contains(%q) = %v, want %v", tt.args.key, got, tt.want)
			}
		})
	}
}

func Test_set_Add(t *testing.T) {
	type args struct {
		key string
	}
	tests := []struct {
		name   string
		keys []string
		args args
		want bool
	}{
		{
			name: "manykeys",
			keys: []string{"1", "2", "3"},
			args: args{key: "1"},
			want: true,
		},
	}
	s := NewSet()
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			for _, key := range tt.keys {
				s.Add(key)
			}

			if got := s.Contains(tt.args.key); got != tt.want {
				t.Errorf("Contains(%q) = %v, want %v", tt.args.key, got, tt.want)
			}
		})
	}
}