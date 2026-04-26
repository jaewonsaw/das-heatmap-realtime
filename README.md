# das-heatmap-realtime

This benchmark reproduces the computational pipeline described in the paper _Near Real-Time Traffic Event Monitoring Using Distributed Acoustic Sensing on an Instrumented Roadway_ using synthetic data.

It preserves:
- FFT size and overlap
- frequency band selection
- spatial section mapping
- temporal smoothing

Synthetic Gaussian noise is used to emulate streaming DAS data, ensuring reproducible evaluation of computational performance (FPS, latency, memory, throughput) independent of site-specific datasets.
