package processor

const (
	threshold = 1000
	maxPrice  = 3000
	minPrice  = 2000
	minRooms  = 2
)

type Interest int

const (
	Interesting Interest = iota
	ClosePrediction
	SkipDistrict
	TooExpensive
	TooCheap
	LowRooms
	Furnished
)

func (i Interest) String() string {
	return [...]string{
		"Interesting",
		"ClosePrediction",
		"SkipDistrict",
		"TooExpensive",
		"TooCheap",
		"LowRooms",
		"Furnished",
	}[i]
}

// emulate sets with map of string->bool
// by default map returns "zero value", false.
var skipDistrict = map[string]bool{ //nolint: gochecknoglobals
	"oakland east":                       true,
	"sunnyvale":                          true,
	"berkeley":                           true,
	"Emeryville":                         true,
	"Larkfield":                          true,
	"berkeley north / hills":             true,
	"oakland downtown":                   true,
	"oakland piedmont / montclair":       true,
	"oakland lake merritt / grand":       true,
	"Oakland":                            true,
	"alameda":                            true,
	"morgan hill":                        true,
	"emeryville":                         true,
	"los gatos":                          true,
	"redwood city":                       true,
	"santa clara":                        true,
	"NORTH OAKLAND TEMESCAL":             true,
	"palo alto":                          true,
	"san jose downtown":                  true,
	"san jose west":                      true,
	"san jose north":                     true,
	"san jose east":                      true,
	"san jose south":                     true,
	"mountain view":                      true,
	"Berkeley":                           true,
	"lafayette / orinda / moraga":        true,
	"fairfield / vacaville":              true,
	"oakland north / temescal":           true,
	"hayward / castro valley":            true,
	"san mateo":                          true,
	"concord / pleasant hill / martinez": true,
	"soquel":                             true,
	"cupertino":                          true,
	"los altos":                          true,
	"healdsburg / windsor":               true,
	"oakland hills / mills":              true,
	"walnut creek":                       true,
	"daly city":                          true,
	"santa rosa":                         true,
	"sonoma":                             true,
	"albany / el cerrito":                true,
	"napa county":                        true,
	"east palo alto":                     true,
	"menlo park":                         true,
	"santa cruz":                         true,
	"rohnert pk / cotati":                true,
	"campbell":                           true,
	"vallejo / benicia":                  true,
	"milpitas":                           true,
	"Santa Clara":                        true,
	"south san francisco":                true,
	"san carlos":                         true,
	"Lake Merritt Oakland":               true,
	"dublin / pleasanton / livermore":    true,
	"burlingame":                         true,
	"oakland rockridge / claremont":      true,
	"Millbrae":                           true,
	"Downtown Oakland":                   true,
	"fremont / union city / newark":      true,
	"san rafael":                         true,
	"West Oakland":                       true,
	"North Oakland":                      true,
	"petaluma":                           true,
	"woodside":                           true,
	"portola valley":                     true,
	"Campbell":                           true,
	"belmont":                            true,
	"San Bruno":                          true,
	"pacifica":                           true,
	"foster city":                        true,
	"oakland west":                       true,
	"tenderloin":                         true,
	"richmond / point / annex":           true,
	"capitola":                           true, //nolint: misspell // this is not a misspell
	//	excludes in SF
	"SOMA / south beach":          true,
	"downtown / civic / van ness": true,
}

// worthNotification rejects non-interesting, expensive items.
func worthNotification(target, prediction extendedRecord) Interest {
	// prediction is close to price
	if (prediction.Price - target.Price) < threshold {
		return ClosePrediction
	}

	// skip some districts
	if skipDistrict[target.District] {
		return SkipDistrict
	}

	// too expensive
	if target.Price > maxPrice {
		return TooExpensive
	}

	// too cheap. strange
	if target.Price < minPrice {
		return TooCheap
	}

	// studio
	if target.Bedrooms < minRooms {
		return LowRooms
	}

	// furnished
	if target.Furnished {
		return Furnished
	}

	return Interesting
}
