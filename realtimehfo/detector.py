"""Reproducible 80–250 Hz ripple-candidate detector."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, find_peaks, sosfiltfilt


def detect(data: np.ndarray, fs: int, start_s: float, labels: list[str]) -> list[dict]:
    """Find short high-RMS bursts containing at least four ripple cycles.

    RMS thresholding follows the basic Staba principle, with an 80–250 Hz
    ripple band, 5 ms RMS, mean + 5 SD threshold, and four positive peaks.
    It is not a validated HFO classifier.
    """
    data = np.asarray(data)
    if data.ndim != 2 or data.shape[1] != len(labels) or fs < 600:
        raise ValueError("Expected samples by channels, matching labels, fs >= 600 Hz")
    if len(data) < fs:
        return []
    sos = butter(4, (80, 250), btype="bandpass", fs=fs, output="sos")
    events = []
    for channel, label in enumerate(labels):
        raw = data[:, channel].astype(np.float64)
        if not np.isfinite(raw).all() or np.std(raw) == 0:
            continue
        filtered = sosfiltfilt(sos, raw)
        rms = np.sqrt(np.maximum(0, uniform_filter1d(filtered**2,
                            size=max(3, round(0.005 * fs)), mode="nearest")))
        threshold = float(np.mean(rms) + 5 * np.std(rms))
        above = rms > threshold
        boundaries = np.flatnonzero(np.diff(np.r_[False, above, False]))
        spans = [[int(a), int(b)] for a, b in boundaries.reshape(-1, 2)]
        merged = []
        for left, right in spans:
            if merged and left - merged[-1][1] <= round(0.01 * fs):
                merged[-1][1] = right
            else:
                merged.append([left, right])
        for left, right in merged:
            duration = (right - left) / fs
            if not 0.006 <= duration <= 0.2:
                continue
            positive, _ = find_peaks(filtered[left:right], distance=max(1, round(fs / 250)))
            if len(positive) < 4:
                continue
            peak = left + int(np.argmax(rms[left:right]))
            events.append({"channel_number": channel + 1, "label": label,
                           "start_s": start_s + left / fs,
                           "peak_s": start_s + peak / fs,
                           "end_s": start_s + right / fs,
                           "score": float(rms[peak]), "threshold": threshold})
    return sorted(events, key=lambda event: (event["peak_s"], event["channel_number"]))
