package processor

const (
	threshold = 500
	maxPrice  = 3000
	minPrice  = 1500
)

var (
	// emulate sets with map of string->bool
	// by default map returns "zero value", false
	skipDistrict = map[string]bool{ //nolint: gochecknoglobals
		"oakland east":           true,
		"san jose downtown":      true,
		"sunnyvale":              true,
		"berkeley":               true,
		"Emeryville":             true,
		"Larkfield":              true,
		"san jose west":          true,
		"berkeley north / hills": true,
		//"oakland lake merritt / grand": true,
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
