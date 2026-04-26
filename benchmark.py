import time
import numpy as np
from scipy.fft import fft, fftfreq
from collections import deque
import psutil
import os
from datetime import datetime

# =========================
# CONFIG (matches instrumented roadway in paper)
# =========================
FFT_SIZE = 1024
FFT_OVERLAP = 0.50
N_CHANNELS = 731
FS = 10e3

FREQ_MIN = -39.063
FREQ_MAX = 117.188

SMOOTH_STEPS = 5
DURATION_SECONDS = 10

# Cable geometry
turns = np.array([19, 108, 197, 286, 375, 464, 553, 642, 731])
NUM_SECTIONS = len(turns) - 2  # 7 sections

# =========================
# ROLLING BUFFER
# =========================
class RollingBuffer:
    def __init__(self, capacity, shape):
        self.capacity = capacity
        self.buffer = np.zeros((capacity, *shape))
        self.index = 0
        self.full = False

    def append(self, data):
        self.buffer[self.index] = data
        self.index = (self.index + 1) % self.capacity
        if self.index == 0:
            self.full = True

    def is_full(self):
        return self.full

    def get(self):
        if not self.full:
            return self.buffer[:self.index]
        return np.concatenate((self.buffer[self.index:], self.buffer[:self.index]))

    def get_last(self, n):
        data = self.get()
        return data[-n:]


# =========================
# PERFORMANCE MONITOR
# =========================
class PerformanceMonitor:
    def __init__(self):
        self.processing_times = deque(maxlen=100)
        self.frame_times = deque(maxlen=100)
        self.memory_usage = deque(maxlen=100)
        self.process = psutil.Process(os.getpid())
        self.data_received = 0
        self.last_log_time = time.perf_counter()

    def update(self, proc_time, frame_time, data_size):
        now = time.perf_counter()

        memory = self.process.memory_info().rss / 1024 / 1024
        self.processing_times.append(proc_time)
        self.frame_times.append(frame_time)
        self.memory_usage.append(memory)
        self.data_received += data_size

        if now - self.last_log_time >= 1.0:
            fps = len(self.frame_times) / (now - self.last_log_time)
            latency = np.mean(self.processing_times) * 1000
            jitter = np.std(self.frame_times) * 1000
            data_rate = self.data_received / (now - self.last_log_time) / 1024
            avg_memory = np.mean(self.memory_usage)

            self.processing_times.clear()
            self.frame_times.clear()
            self.memory_usage.clear()
            self.data_received = 0
            self.last_log_time = now

            return {
                "timestamp": datetime.now().isoformat(),
                "fps": fps,
                "latency": latency,
                "data_rate": data_rate,
                "jitter": jitter,
                "memory": avg_memory
            }
        return None


# =========================
# FBE COMPUTATION
# =========================
def compute_fbe(buffer, window, scaling, freq_mask):
    temp = buffer - np.mean(buffer, axis=0)
    temp *= window

    fft_result = fft(temp, axis=0)
    power = np.abs(fft_result) ** 2
    power[1:] *= 2  # one-sided correction

    return scaling * np.mean(power[freq_mask], axis=0)


# =========================
# GEOMETRY HANDLING
# =========================
def split_and_flip_sections(fbe_vector):
    out = np.copy(fbe_vector)

    for i in range(1, NUM_SECTIONS, 2):
        segment = fbe_vector[turns[i]:turns[i+1]+1]
        out[turns[i]:turns[i+1]+1] = np.flip(segment)

    return out


def reshape_sections(fbe_vector):
    sections = []
    for i in range(NUM_SECTIONS):
        section = fbe_vector[turns[i]:turns[i+1]+1]
        sections.append(section)
    return np.stack(sections, axis=1)  # shape ~ (length, sections)


# =========================
# MAIN BENCHMARK
# =========================
def run_benchmark():

    print("Starting benchmark (paper-consistent version)...")

    fft_buffer = RollingBuffer(FFT_SIZE, (N_CHANNELS,))
    fbe_buffer = RollingBuffer(SMOOTH_STEPS, (90, NUM_SECTIONS))  # ~90 x 7

    window = np.hanning(FFT_SIZE).reshape(-1, 1)
    scaling = (1.633333**2) / (FFT_SIZE * FS)

    freq = fftfreq(FFT_SIZE, d=1 / FS)
    freq_mask = (freq >= FREQ_MIN) & (freq <= FREQ_MAX)

    overlap_window = int(FFT_SIZE * FFT_OVERLAP)
    fft_step = FFT_SIZE - overlap_window

    monitor = PerformanceMonitor()

    start_time = time.perf_counter()

    while time.perf_counter() - start_time < DURATION_SECONDS:

        frame_start = time.perf_counter()

        # --- Simulate streaming DAS data ---
        for _ in range(fft_step):
            sample = np.random.randn(N_CHANNELS)
            fft_buffer.append(sample)

        if not fft_buffer.is_full():
            continue

        process_start = time.perf_counter()

        # --- FBE computation ---
        fbe = compute_fbe(
            fft_buffer.get(),
            window,
            scaling,
            freq_mask
        )

        # --- Geometry mapping ---
        fbe_flipped = split_and_flip_sections(fbe)
        fbe_sections = reshape_sections(fbe_flipped)

        # --- Temporal smoothing ---
        fbe_buffer.append(fbe_sections)
        smoothed = np.mean(fbe_buffer.get_last(SMOOTH_STEPS), axis=0)

        proc_time = time.perf_counter() - process_start
        frame_time = time.perf_counter() - frame_start

        metrics = monitor.update(
            proc_time,
            frame_time,
            N_CHANNELS * 8  # approximate bytes
        )

        if metrics:
            print(
                f"[{metrics['timestamp']}] "
                f"FPS={metrics['fps']:.2f} | "
                f"Latency={metrics['latency']:.2f} ms | "
                f"Rate={metrics['data_rate']:.2f} kB/s | "
                f"Mem={metrics['memory']:.2f} MB"
            )

    print("Benchmark complete.")


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    run_benchmark()