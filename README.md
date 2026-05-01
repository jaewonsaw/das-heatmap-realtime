# das-heatmap-realtime

This repository provides a minimal reproducible reference implementation of the processing pipeline described in the paper _Near Real-Time Traffic Event Monitoring Using Distributed Acoustic Sensing on an Instrumented Roadway_. This repository supports the quantitative performance analysis presented in the manuscript.

## Synthetic data

The included `benchmark.py` script is designed to reproduce the computational behavior of the system using synthetic streaming data. It uses Gaussian noise to simulate DAS phase measurements. This allows reproducible evaluation of computational performance without requiring access to proprietary datasets or site-specific infrastructure.

## Performance metrics

The benchmark reports:

- Frame rate (FPS)
- Processing latency
- Data throughput
- Memory usage

These metrics are computed using the same definitions described in the manuscript.

## Scope of the benchmark
This repository is designed to reproducibly evaluate the core computational performance of the visualization pipeline, rather than the full deployed system.

The benchmark intentionally excludes:
- Socket-based data acquisition
- File I/O (CBT parsing)
- Graphical user interface (GUI) rendering

These components introduce system- and hardware-dependent variability that is difficult to reproduce consistently across environments. Instead, the benchmark isolates the signal processing and data handling pipeline, including:
- FFT-based Frequency Band Energy (FBE) computation
- Rolling buffer management
- Spatial mapping based on cable geometry
- Temporal smoothing

All algorithmic parameters (FFT size, overlap, frequency band, smoothing, and cable geometry) are consistent with those used in the manuscript. This allows reproducible evaluation of the performance metrics listed above.

## Relationship to Manuscript Results

The performance reported in the manuscript reflects end-to-end system behavior, including data acquisition and visualization overhead. In contrast, this benchmark reports algorithm-level performance. As a result, the benchmark may achieve higher frame rates and lower latency than the full system.

## How to Run

Install dependencies and run the benchmark:

```bash
pip install -r requirements.txt
python benchmark.py
