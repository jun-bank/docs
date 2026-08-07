package main

import (
	"fmt"
	"runtime"
	"sync"
)

func main() {
	var m0, m1 runtime.MemStats
	runtime.GC()
	runtime.ReadMemStats(&m0)

	const N = 100000
	var wg sync.WaitGroup
	stop := make(chan struct{})
	wg.Add(N)
	for i := 0; i < N; i++ {
		go func() { defer wg.Done(); <-stop }()
	}
	for runtime.NumGoroutine() < N {
	}
	runtime.ReadMemStats(&m1)
	fmt.Printf("goroutines=%d  heap delta=%.1f MB  per-goroutine=%.0f bytes\n",
		runtime.NumGoroutine(), float64(m1.HeapAlloc-m0.HeapAlloc)/1e6,
		float64(m1.HeapAlloc-m0.HeapAlloc)/N)
	fmt.Printf("OS threads (GOMAXPROCS=%d)\n", runtime.GOMAXPROCS(0))
	close(stop)
	wg.Wait()
}
