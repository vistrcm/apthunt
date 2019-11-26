package thumber

//it looks like struct{} takes no space, so going to use it to implement sets
type void struct{}

// actual set structure
type set struct {
	m map[string]void
}

//NewSet create new set
func NewSet() *set {
	return &set{m: make(map[string]void)}
}

//Add adds key to the set
func (s *set) Add(key string) {
	//empty struct as value for existance
	var exists = struct{}{}

	s.m[key] = exists
}

//Contains returns true if key exists in the set
func (s *set) Contains(key string) bool {
	_, exists := s.m[key]
	return exists
}
