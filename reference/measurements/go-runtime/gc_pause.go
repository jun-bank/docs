package main

import (
	"fmt"
	"runtime"
	"runtime/debug"
	"time"
)

var sink [][]byte

func main() {
	live := make([][]*int, 1000)
	for i := range live {
		s := make([]*int, 1000)
		for j := range s {
			v := j
			s[j] = &v
		}
		live[i] = s
	}
	var ms0 runtime.MemStats
	runtime.ReadMemStats(&ms0)
	fmt.Printf("live heap: %.1f MB\n", float64(ms0.HeapAlloc)/1e6)

	var s0 debug.GCStats
	debug.ReadGCStats(&s0)
	start := time.Now()
	deadline := start.Add(5 * time.Second)
	for time.Now().Before(deadline) {
		sink = append(sink, make([]byte, 4096))
		if len(sink) > 2000 {
			sink = sink[:0]
		}
	}
	elapsed := time.Since(start)
	var s1 debug.GCStats
	s1.PauseQuantiles = make([]time.Duration, 5)
	debug.ReadGCStats(&s1)
	var ms runtime.MemStats
	runtime.ReadMemStats(&ms)
	n := s1.NumGC - s0.NumGC
	fmt.Printf("GC cycles in %v: %d\n", elapsed.Round(time.Millisecond), n)
	fmt.Printf("STW pause quantiles (min/25/50/75/max): %v\n", s1.PauseQuantiles)
	fmt.Printf("STW total: %v  (= %.4f%% of wall clock)\n", s1.PauseTotal, float64(s1.PauseTotal)/float64(elapsed)*100)
	fmt.Printf("GC CPU fraction: %.3f%%\n", ms.GCCPUFraction*100)
	runtime.KeepAlive(live)
}
