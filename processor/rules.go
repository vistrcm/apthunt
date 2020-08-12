package processor

const (
	threshold = 600
	maxPrice  = 3500
	minPrice  = 2000
)

var (
	// emulate sets with map of string->bool
	// by default map returns "zero value", false
	skipDistrict = map[string]bool{ //nolint: gochecknoglobals
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
	}
)

// worthNotification rejects non-interesting, expensive items.
func worthNotification(target, prediction extendedRecord) bool {
	// prediction is close to price
	if (prediction.Price - target.Price) < threshold {
		return false
	}

	// skip some districts
	if skipDistrict[target.District] {
		return false
	}

	// too expensive
	if target.Price > maxPrice {
		return false
	}

	// too cheap. strange
	if target.Price < minPrice {
		return false
	}

	return true
}
