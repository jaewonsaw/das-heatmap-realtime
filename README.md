# das-heatmap-realtime

This repository provides a minimal reference implementation of the processing pipeline described in the paper _Near Real-Time Traffic Event Monitoring Using Distributed Acoustic Sensing on an Instrumented Roadway_. The included `benchmark.py` script is designed to reproduce the computational behavior of the system (FFT-based Frequency Band Energy extraction, buffering, and spatial mapping) using synthetic streaming data.

## Synthetic Data

The benchmark uses Gaussian noise to simulate DAS phase measurements. This allows reproducible evaluation of computational performance without requiring access to proprietary datasets or site-specific infrastructure.

## Performance Metrics

The benchmark reports:

- Frame rate (FPS)
- Processing latency
- Data throughput
- Memory usage

These metrics are computed using the same definitions described in the manuscript.

## Clarification on Performance

The performance observed in this benchmark may be higher than the values reported in the manuscript. This is expected. The benchmark isolates the core signal processing pipeline and excludes several components present in the full system, including:

- Socket-based data streaming
- File I/O (CBT parsing)
- Visualization rendering (GUI)
- Logging and system-level overhead

As a result, the benchmark reflects **algorithm-level performance**, whereas the manuscript reports **end-to-end system performance**. The benchmark implementation preserves FFT size and overlap, frequency band selection, temporal smoothing, and section-based spatial mapping (snake geometry).
