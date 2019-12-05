package thumber

//it looks like struct{} takes no space, so going to use it to implement sets
type void struct{}

// actual Set structure
type Set struct {
	m map[string]void
}

//NewSet create new Set
func NewSet() *Set {
	return &Set{m: make(map[string]void)}
}

//Add adds key to the Set
func (s *Set) Add(key string) {
	//empty struct as value for existence
	var exists = struct{}{}

	s.m[key] = exists
}

//Contains returns true if key exists in the Set
func (s *Set) Contains(key string) bool {
	_, exists := s.m[key]
	return exists
}
