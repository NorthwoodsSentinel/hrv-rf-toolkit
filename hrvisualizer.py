#!/usr/bin/env python3
"""
HRVisualizer – Python/PySide6 port of the original VB.NET HRVisualizer.
Reads NeXus .txt export files (256 Hz ECG + breathing) and displays HRV analysis.

Usage:
    python hrvisualizer.py [file.txt]
    python hrvisualizer.py          # shows drag-and-drop window

Dependencies (all in every-breath-you-take venv):
    pip install pyqtgraph
"""

import sys
import math
import numpy as np
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QScrollBar, QFileDialog, QMessageBox, QLabel, QSizePolicy,
)
from PySide6.QtCore import Qt, QMimeData, QThread, Signal, QObject
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QKeySequence, QImage, QClipboard
import pyqtgraph as pg
from scipy.interpolate import CubicSpline

# ─── Constants (matching VB originals) ────────────────────────────────────────
SPS         = 256           # samples per second
LOOKAHEAD   = 3 * SPS       # R-wave search window (samples)
SINE_WIN_S  = 60            # sine-fit window half-width (seconds)
YSCALE      = 150.0         # y-axis half-range

# ─── Signal processing ────────────────────────────────────────────────────────

def load_file(path: str):
    """
    Parse a NeXus .txt export file.
    Returns (ecg, br) as float64 numpy arrays at 256 Hz.
    Raises ValueError if the header is invalid.
    """
    header_items = 0
    in_data = False
    ecg_vals, br_vals = [], []

    with open(path, encoding="ascii", errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not in_data:
                if   line.startswith("Client"):      header_items += 1
                elif line.startswith("Session"):     header_items += 1
                elif line.startswith("Date"):        header_items += 1
                elif line.startswith("Time"):        header_items += 1
                elif line.startswith("Output rate"):
                    header_items += 1
                    if "256" in line:
                        header_items += 1
                elif line.startswith("Sensor"):
                    in_data = True
            else:
                parts = line.replace(",", "\t").split("\t")
                if 2 <= len(parts) <= 4:
                    try:
                        ecg_vals.append(float(parts[0]))
                        br_vals.append(float(parts[1]))
                    except ValueError:
                        pass

    if header_items != 6:
        raise ValueError(
            f"Not a valid NeXus export file (found {header_items} header items, expected 6)."
        )
    return np.array(ecg_vals, dtype=np.float64), np.array(br_vals, dtype=np.float64)


def lowess2(x: np.ndarray, y: np.ndarray, n_pts: int) -> np.ndarray:
    """
    LOWESS2 – Locally Weighted Scatterplot Smoothing, sparse→sparse.
    Direct port of Smooth.vb Lowess2().
    x, y : 1-D arrays of same length (sorted by x)
    Returns smoothed z, same length.
    """
    n = len(x)
    z = np.zeros(n)

    for i_pt in range(n):
        x_now = x[i_pt]
        distances = np.abs(x - x_now)

        # Window-shrinking: keep n_pts nearest (contiguous in sorted x)
        i_min, i_max = 0, n - 1
        while (i_max + 1 - i_min) > n_pts:
            if distances[i_min] > distances[i_max]:
                i_min += 1
            elif distances[i_min] < distances[i_max]:
                i_max -= 1
            else:
                i_min += 1
                i_max -= 1

        xi = x[i_min : i_max + 1]
        yi = y[i_min : i_max + 1]
        di = distances[i_min : i_max + 1]

        max_dist = np.max(di)
        if max_dist == 0.0:
            z[i_pt] = y[i_pt]
            continue

        wi      = (1.0 - (di / max_dist) ** 3) ** 3
        sum_w   = np.sum(wi)
        sum_wx  = np.dot(wi, xi)
        sum_wx2 = np.dot(wi, xi * xi)
        sum_wy  = np.dot(wi, yi)
        sum_wxy = np.dot(wi, xi * yi)
        denom   = sum_w * sum_wx2 - sum_wx ** 2

        if denom != 0.0:
            slope     = (sum_w * sum_wxy - sum_wx * sum_wy) / denom
            intercept = (sum_wx2 * sum_wy - sum_wx * sum_wxy) / denom
            z[i_pt]   = slope * x_now + intercept
        else:
            z[i_pt] = y[i_pt]

    return z


def filter_breath(br: np.ndarray):
    """
    Chebyshev 1st-order high-pass filter, fc=0.05 Hz @ 256 sps.
    Port of CodeFile.vb FilterBreathData().
    Returns (filtered_br, br_rms).
    """
    n = len(br)
    out = np.empty(n)
    xv1 = br[0]
    yv1 = 0.0
    rms_sum = 0.0
    rms_count = 0
    skip = 30 * SPS

    for i in range(n):
        xv0  = xv1
        xv1  = br[i] / 1.000312225
        yv0  = yv1
        yv1  = xv1 - xv0 + 0.9993757454 * yv0
        out[i] = yv1
        if i > skip:
            rms_sum += yv1 * yv1
            rms_count += 1

    br_rms = math.sqrt(rms_sum / rms_count) if rms_count else 0.0
    return out, br_rms


def find_breath_peaks(br: np.ndarray):
    """
    Alternately locate breath inhale peaks and exhale troughs.
    Port of CodeFile.vb FindBreathPeaks().
    Returns (peak_times, peak_vals) as int/float arrays.
    """
    n = len(br)
    init_n = min(SPS * 60, n)
    filtered_val = float(np.mean(br[:init_n]))

    peak_times, peak_vals = [], []
    idx = 0
    looking_pos = True

    while idx < n:
        if looking_pos:
            local_max = -math.inf
            peak_idx  = idx
            while idx < n:
                val = br[idx]
                filtered_val = filtered_val * 0.99 + val * 0.01
                if val > local_max:
                    local_max = val
                    peak_idx  = idx
                idx += 8
                if val < filtered_val:
                    break
            peak_times.append(peak_idx)
            peak_vals.append(local_max)
            looking_pos = False
        else:
            local_min = math.inf
            peak_idx  = idx
            while idx < n:
                val = br[idx]
                filtered_val = filtered_val * 0.99 + val * 0.01
                if val < local_min:
                    local_min = val
                    peak_idx  = idx
                idx += 8
                if val > filtered_val:
                    break
            peak_times.append(peak_idx)
            peak_vals.append(local_min)
            looking_pos = True

    return np.array(peak_times, dtype=np.int64), np.array(peak_vals)


def measure_breath_excursions(pbr_times: np.ndarray, pbr_vals: np.ndarray):
    """
    Compute LOWESS-smoothed breath amplitude envelope, rescaled to ±YSCALE.
    Port of CodeFile.vb MeasureBreathExcursions().
    Returns (br_val, br_avg) where br_val is the rescaled envelope at each peak pair.
    """
    last_bp = len(pbr_times) - 1
    if last_bp < 1:
        return np.zeros(1), 0.0

    br_val_raw = np.abs(np.diff(pbr_vals[:last_bp + 1]))   # peak-to-peak amplitudes
    br_sum  = np.sum(br_val_raw[pbr_times[:last_bp] > 30 * SPS])
    br_cnt  = np.sum(pbr_times[:last_bp] > 30 * SPS)
    br_avg  = float(br_sum / br_cnt) if br_cnt else 0.0

    br_vals_smooth = lowess2(
        pbr_times[:last_bp].astype(np.float64),
        br_val_raw,
        17,
    )

    skip = 4
    if last_bp > skip:
        valid = br_vals_smooth[skip:]
        br_max = np.max(valid)
        br_min = np.min(valid)
    else:
        br_max = np.max(br_vals_smooth)
        br_min = np.min(br_vals_smooth)

    rng = br_max - br_min
    if rng > 0:
        scale = 1.98 * YSCALE / rng
        br_val = (br_vals_smooth - br_min) * scale - YSCALE
    else:
        br_val = np.zeros(last_bp)

    return br_val, br_avg


def process_raw_ekg(ecg: np.ndarray):
    """
    Detect R-waves using weighted dv/dt + ROI peak search.
    Port of CodeFile.vb Process_Raw_EKG().
    Returns rwave_events: sparse array where rwave_events[i] = IBI in samples (0 elsewhere).
    """
    n = len(ecg)
    dvdt = np.zeros(n)

    # Weighted dv/dt differentiator (history-weighted high-pass)
    t0 = t1 = t2 = float(ecg[0])
    for i in range(3, n):
        dvdt[i - 3] = (t0 * 1.0 + t1 * 0.5 + t2 * 0.25) / 1.75 - ecg[i]
        t0, t1, t2 = t1, t2, float(ecg[i])

    # 5-point centre average (ROI)
    roi = np.zeros(n)
    for i in range(2, n - 2):
        roi[i] = (dvdt[i-2] + dvdt[i-1] + dvdt[i] + dvdt[i+1] + dvdt[i+2]) / 5.0

    rwave_events = np.zeros(n)

    # Initial peak in first LOOKAHEAD window
    end0     = min(LOOKAHEAD, n)
    peak_max = float(np.max(roi[:end0]))

    scan_point  = 0
    prior_rpoint = 0

    while scan_point + LOOKAHEAD < n:
        peak_max *= 0.7
        peak_point = 0

        # PeakSearch: scan for ROI peak above threshold
        while True:
            end_scan = min(scan_point + LOOKAHEAD, n)
            for i in range(scan_point, end_scan):
                if roi[i] > peak_max:
                    peak_max  = roi[i]
                    peak_point = i
                elif peak_point:
                    break

            if peak_point:
                break
            peak_max *= 0.95   # lower threshold and retry

        # Fine-locate R-wave max in dvdt within ±2 samples
        r_max   = 0.0
        r_point = peak_point
        lo = max(0, peak_point - 2)
        hi = min(n - 1, peak_point + 2)
        for i in range(lo, hi + 1):
            if dvdt[i] > r_max:
                r_max   = dvdt[i]
                r_point = i

        if prior_rpoint:
            rwave_events[r_point] = r_point - prior_rpoint

        prior_rpoint = r_point
        scan_point   = r_point + 20

    return rwave_events


def remove_ectopic_beats(rwave_events: np.ndarray, n: int) -> None:
    """
    Detect and correct PVC ectopic beats (modifies rwave_events in-place).
    Port of CodeFile.vb RemoveEctopicBeats().
    """
    while True:
        positions = np.nonzero(rwave_events[:n])[0]
        if len(positions) < 5:
            break

        runs = np.diff(positions.astype(np.int64))
        prev_run = 0
        d1 = d2 = d3 = 0
        fixed = False

        anchor1 = anchor2 = anchor3 = 0

        for k in range(len(runs)):
            anchor1 = anchor2
            anchor2 = anchor3
            anchor3 = int(positions[k])
            this_run = int(runs[k])

            if prev_run:
                d1, d2, d3 = d2, d3, this_run - prev_run

                if d1 < 0 and d2 > 0 and d3 < 0:
                    if abs(d2 + d1 + d3) < d2 * 0.1:
                        anchor_next = int(positions[k + 1]) if k + 1 < len(positions) else n
                        rwave_events[anchor2] = 0
                        new_pos = (anchor1 + anchor_next) // 2
                        rwave_events[new_pos]    = new_pos - anchor1
                        rwave_events[anchor_next] = anchor_next - new_pos
                        fixed = True
                        break

            prev_run = this_run

        if not fixed:
            break


def build_rwave_arrays(rwave_events: np.ndarray, n: int):
    """
    Collect R-wave times and inter-beat intervals from the sparse events array.
    Returns (rwave_time, rwave_ibi) as int64 and float64 arrays.
    """
    positions = np.nonzero(rwave_events[:n])[0]
    ibi_vals  = rwave_events[positions]
    return positions.astype(np.int64), ibi_vals.astype(np.float64)


def rebase_and_invert(rwave_time: np.ndarray, rwave_ibi: np.ndarray):
    """
    LOWESS-detrend the IBI curve, then invert (smooth - raw).
    Positive peaks in the result correspond to high HRV moments.
    Port of CodeFile.vb RebaseAndInvertRwaves().
    Returns rwave_val (detrended, inverted HRV signal).
    """
    smoothed = lowess2(rwave_time.astype(np.float64), rwave_ibi, 41)
    return smoothed - rwave_ibi


def find_hrv_peaks(rwave_time: np.ndarray, rwave_val: np.ndarray):
    """
    Alternately find positive and negative HRV peaks using zero-crossings.
    Port of CodeFile.vb FindHrvPeaks().
    Returns (peak_time, peak_val).
    """
    n = len(rwave_val)
    peak_times, peak_vals = [], []
    idx = 0

    while True:
        # ── positive peak ──────────────────────────────────────────
        local_max = -math.inf
        peak_idx  = -1
        while idx < n:
            val = rwave_val[idx]
            if val > local_max:
                local_max = val
                peak_idx  = int(rwave_time[idx])
            idx += 1
            if val < 0:
                break
        else:
            if peak_idx >= 0:
                peak_times.append(peak_idx)
                peak_vals.append(local_max)
            break
        if peak_idx >= 0:
            peak_times.append(peak_idx)
            peak_vals.append(local_max)

        # ── negative peak ──────────────────────────────────────────
        local_min = math.inf
        peak_idx  = -1
        while idx < n:
            val = rwave_val[idx]
            if val < local_min:
                local_min = val
                peak_idx  = int(rwave_time[idx])
            idx += 1
            if val > 0:
                break
        else:
            if peak_idx >= 0:
                peak_times.append(peak_idx)
                peak_vals.append(local_min)
            break
        if peak_idx >= 0:
            peak_times.append(peak_idx)
            peak_vals.append(local_min)

    return np.array(peak_times, dtype=np.int64), np.array(peak_vals)


def measure_peak_to_peak(peak_time: np.ndarray, peak_val: np.ndarray):
    """
    Compute LOWESS-smoothed HRV amplitude envelope.
    Port of CodeFile.vb MeasurePeakToPeak().
    Returns (rr_val, peak_point) where rr_val is the rescaled envelope
    and peak_point is the sample index of maximum HRV amplitude.
    """
    last_peak = len(peak_val) - 1   # number of amplitude measurements
    if last_peak < 2:
        return np.zeros(1), 0

    rr_val_raw = np.abs(np.diff(peak_val[:last_peak + 1]))   # last_peak elements

    rr_vals_smooth = lowess2(
        peak_time[:last_peak].astype(np.float64),
        rr_val_raw,
        17,
    )

    skip = 4
    if last_peak > skip:
        valid = rr_vals_smooth[skip:]
        rr_max = np.max(valid)
        rr_min = np.min(valid)
    else:
        rr_max = np.max(rr_vals_smooth)
        rr_min = np.min(rr_vals_smooth)

    rng = rr_max - rr_min
    if rng > 0:
        scale  = 1.98 * YSCALE / rng
        rr_val = (rr_vals_smooth - rr_min) * scale - YSCALE
    else:
        rr_val = np.zeros(last_peak)

    # Find the sample with maximum HRV amplitude
    best_idx  = int(np.argmax(rr_val))
    peak_point = int(peak_time[best_idx])

    return rr_val, peak_point


def rescale_symmetric(arr: np.ndarray, skip: int = 0) -> np.ndarray:
    """Rescale array so max absolute value = 0.98 * YSCALE."""
    if len(arr) <= skip:
        abs_max = np.max(np.abs(arr))
    else:
        abs_max = np.max(np.abs(arr[skip:]))
    if abs_max == 0:
        return arr
    scale = YSCALE * 0.98 / abs_max
    return arr * scale


def _get_error(phase: float, omega: float, amplitude: float, offset: float,
               br_win: np.ndarray) -> float:
    """L1 error between cosine fit and breathing window. Vectorised."""
    phases = phase + omega * np.arange(len(br_win))
    return float(np.sum(np.abs(amplitude * np.cos(phases) + offset - br_win)))


def sine_wave_fit(br: np.ndarray, peak_point: int):
    """
    Fit a cosine to the ±SINE_WIN_S second window around peak_point.
    Port of CodeFile.vb SineWaveFit().
    Returns (resonance_bpm, sine_x, sine_y) where sine_x/y are the fitted curve arrays.
    """
    n = len(br)
    half = SINE_WIN_S * SPS // 2
    first = max(0, peak_point - half)
    last  = min(n - 1, peak_point + half)
    win   = br[first : last + 1]

    cos_scale  = (np.max(win) - np.min(win)) / 2.0
    cos_offset = (np.max(win) + np.min(win)) / 2.0

    pi = math.pi

    # ── Coarse search: bpm 3.5 → 7.0, phase 0 and π ──────────────────────────
    min_error = math.inf
    min_phase = 0.0
    min_omega = 2.0 * pi / 60.0 * 4.0 / SPS   # fallback

    for bpm in np.arange(3.5, 7.01, 0.5):
        omega = 2.0 * pi / 60.0 * bpm / SPS
        for j in range(2):
            phase = pi * j
            err   = _get_error(phase, omega, cos_scale, cos_offset, win)
            if err < min_error:
                min_error = err
                min_phase = phase
                min_omega = omega

    phase = min_phase
    omega = min_omega

    # ── Coordinate descent until convergence ─────────────────────────────────
    while True:
        corrections = 0

        # 1. Phase
        last_err   = _get_error(phase, omega, cos_scale, cos_offset, win)
        phase_step = pi / 100.0
        if last_err < _get_error(phase + phase_step, omega, cos_scale, cos_offset, win):
            phase_step = -phase_step
        for _ in range(200):
            phase    += phase_step
            this_err  = _get_error(phase, omega, cos_scale, cos_offset, win)
            if last_err < this_err:
                break
            last_err = this_err
            corrections += 1
        phase -= phase_step

        # 2. Omega (frequency)
        last_err   = _get_error(phase, omega, cos_scale, cos_offset, win)
        omega_step = 1.001
        if last_err < _get_error(phase, omega * omega_step, cos_scale, cos_offset, win):
            omega_step = 1.0 / omega_step
        for _ in range(400):
            omega    *= omega_step
            this_err  = _get_error(phase, omega, cos_scale, cos_offset, win)
            if last_err < this_err:
                break
            last_err = this_err
            corrections += 1
        omega /= omega_step

        # 3. DC offset
        last_err    = _get_error(phase, omega, cos_scale, cos_offset, win)
        offset_step = 1.0
        if last_err < _get_error(phase, omega, cos_scale, cos_offset + offset_step, win):
            offset_step = -1.0
        for _ in range(200):
            cos_offset += offset_step
            this_err    = _get_error(phase, omega, cos_scale, cos_offset, win)
            if last_err < this_err:
                break
            last_err = this_err
            corrections += 1
        cos_offset -= offset_step

        # 4. Amplitude
        last_err  = _get_error(phase, omega, cos_scale, cos_offset, win)
        amp_step  = 1.005
        if last_err < _get_error(phase, omega, cos_scale * amp_step, cos_offset, win):
            amp_step = 1.0 / amp_step
        for _ in range(999):
            cos_scale *= amp_step
            this_err   = _get_error(phase, omega, cos_scale, cos_offset, win)
            if last_err < this_err:
                break
            last_err = this_err
            corrections += 1
        cos_scale /= amp_step

        if corrections == 0:
            break

    # Build fitted sine array
    phases_arr = phase + omega * np.arange(len(win))
    sine_y     = cos_scale * np.cos(phases_arr) + cos_offset
    sine_x     = np.arange(first, first + len(win))

    resonance_bpm = omega / (2.0 * pi) * 60.0 * SPS
    return resonance_bpm, sine_x, sine_y


# ─── Data container ───────────────────────────────────────────────────────────

@dataclass
class HRVData:
    name:          str         = ""
    n_samples:     int         = 0

    br:            np.ndarray  = field(default_factory=lambda: np.array([]))
    ecg_raw:       np.ndarray  = field(default_factory=lambda: np.array([]))

    rwave_time:    np.ndarray  = field(default_factory=lambda: np.array([], dtype=np.int64))
    rwave_val:     np.ndarray  = field(default_factory=lambda: np.array([]))   # detrended HRV

    rr_val:        np.ndarray  = field(default_factory=lambda: np.array([]))   # HRV amplitude envelope
    peak_time:     np.ndarray  = field(default_factory=lambda: np.array([], dtype=np.int64))

    br_val:        np.ndarray  = field(default_factory=lambda: np.array([]))   # breath excursion envelope
    pbr_times:     np.ndarray  = field(default_factory=lambda: np.array([], dtype=np.int64))

    sine_x:        np.ndarray  = field(default_factory=lambda: np.array([]))
    sine_y:        np.ndarray  = field(default_factory=lambda: np.array([]))

    peak_point:    int         = 0
    resonance_bpm: float       = 0.0
    br_avg:        float       = 0.0


# ─── Full processing pipeline ─────────────────────────────────────────────────

def process_file(path: str, status_cb=None) -> HRVData:
    """Run the complete HRV analysis pipeline. Returns an HRVData object."""

    def status(msg):
        if status_cb:
            status_cb(msg)

    status("Loading file…")
    ecg, br = load_file(path)
    n = len(ecg)

    status("Filtering breathing…")
    br, _br_rms = filter_breath(br)

    status("Finding breath peaks…")
    pbr_times, pbr_vals = find_breath_peaks(br)

    status("Measuring breath excursions…")
    br_val, br_avg = measure_breath_excursions(pbr_times, pbr_vals)
    last_bp = len(pbr_times) - 1

    status("Detecting R-waves…")
    rwave_events = process_raw_ekg(ecg)

    status("Removing ectopic beats…")
    remove_ectopic_beats(rwave_events, n)

    rwave_time, rwave_ibi = build_rwave_arrays(rwave_events, n)

    status("Detrending HRV…")
    rwave_val = rebase_and_invert(rwave_time, rwave_ibi)

    status("Finding HRV peaks…")
    peak_time, peak_val = find_hrv_peaks(rwave_time, rwave_val)

    status("Measuring peak-to-peak…")
    rr_val, peak_point = measure_peak_to_peak(peak_time, peak_val)
    last_peak = len(peak_val) - 1

    status("Rescaling…")
    br       = rescale_symmetric(br)
    rwave_val = rescale_symmetric(rwave_val)

    status("Fitting sine wave…")
    resonance_bpm, sine_x, sine_y = sine_wave_fit(br, peak_point)

    status("Done.")

    data              = HRVData()
    data.name         = Path(path).stem
    data.n_samples    = n
    data.br           = br
    data.ecg_raw      = ecg
    data.rwave_time   = rwave_time
    data.rwave_val    = rwave_val
    data.rr_val       = rr_val
    data.peak_time    = peak_time[:last_peak]
    data.br_val       = br_val
    data.pbr_times    = pbr_times[:last_bp]
    data.sine_x       = sine_x
    data.sine_y       = sine_y
    data.peak_point   = peak_point
    data.resonance_bpm = resonance_bpm
    data.br_avg       = br_avg
    return data


# ─── Worker thread ────────────────────────────────────────────────────────────

class Worker(QObject):
    finished = Signal(object)   # HRVData or Exception
    status   = Signal(str)

    def __init__(self, path: str):
        super().__init__()
        self.path = path

    def run(self):
        try:
            data = process_file(self.path, status_cb=self.status.emit)
            self.finished.emit(data)
        except Exception as exc:
            self.finished.emit(exc)


# ─── Chart widget ─────────────────────────────────────────────────────────────

class HRVChart(pg.PlotWidget):
    """PlotWidget that forwards wheel events to the parent window."""

    def wheelEvent(self, event):
        event.ignore()          # let the parent QMainWindow handle it


# ─── Main window ─────────────────────────────────────────────────────────────

class HRVWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HRVisualizer")
        self.resize(1200, 500)
        self.setAcceptDrops(True)

        self.data:     Optional[HRVData] = None
        self._monochrome = False
        self._time_scale = True
        self._span   = 0      # visible span in samples
        self._first  = 0      # first visible sample

        # ── Central layout ──────────────────────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # ── Drop label (shown before file loaded) ───────────────────────────
        self._drop_label = QLabel(
            "Drag and drop a NeXus .txt export file here\n"
            "or use  File → Open"
        )
        self._drop_label.setAlignment(Qt.AlignCenter)
        self._drop_label.setStyleSheet(
            "QLabel { color: #888; font-size: 18px; border: 3px dashed #ccc; border-radius: 12px; }"
        )
        layout.addWidget(self._drop_label)

        # ── Chart ───────────────────────────────────────────────────────────
        pg.setConfigOptions(antialias=True)
        self._chart = HRVChart(background="w")
        self._chart.setVisible(False)
        self._chart.setMouseEnabled(x=False, y=False)
        self._chart.showGrid(x=False, y=False)
        self._chart.getPlotItem().hideAxis("left")
        self._chart.getPlotItem().hideAxis("bottom")

        vb = self._chart.getViewBox()
        vb.setYRange(-YSCALE, YSCALE * 1.1, padding=0)
        vb.setLimits(yMin=-YSCALE * 1.05, yMax=YSCALE * 1.15)

        layout.addWidget(self._chart, stretch=1)

        # ── Scrollbar ───────────────────────────────────────────────────────
        self._scroll = QScrollBar(Qt.Horizontal)
        self._scroll.setVisible(False)
        self._scroll.valueChanged.connect(self._on_scroll)
        layout.addWidget(self._scroll)

        # ── Trace items ─────────────────────────────────────────────────────
        self._p_br    = self._chart.plot(pen=pg.mkPen("b", width=2))     # breathing
        self._p_hr    = self._chart.plot(pen=pg.mkPen("r", width=2))     # HR detrended (spline)
        self._p_trend = self._chart.plot(pen=pg.mkPen("#00cc00", width=4))  # HRV envelope
        self._p_btrend = self._chart.plot(
            pen=pg.mkPen("orange", width=4, style=Qt.DashLine))          # breath envelope
        self._p_sine  = self._chart.plot(
            pen=pg.mkPen((180, 180, 180), width=10))                     # sine fit
        self._p_tick  = self._chart.plot(
            pen=pg.mkPen("k", width=2, style=Qt.DashLine))              # peak marker
        self._p_label = pg.TextItem(anchor=(0.5, 0.0), color="k")
        self._chart.addItem(self._p_label)

        # ── Time-axis tick items ─────────────────────────────────────────────
        self._tick_items = []   # list of (InfiniteLine, TextItem)

        # ── Menu bar ────────────────────────────────────────────────────────
        self._build_menu()

        # ── Status bar ──────────────────────────────────────────────────────
        self.statusBar().showMessage("Open a file or drag one in.")

    # ── Menu ──────────────────────────────────────────────────────────────────

    def _build_menu(self):
        mb = self.menuBar()

        # File
        fm = mb.addMenu("&File")
        a = QAction("&Open…", self, shortcut=QKeySequence.Open)
        a.triggered.connect(self._open_dialog)
        fm.addAction(a)
        fm.addSeparator()
        a = QAction("E&xit", self, shortcut=QKeySequence.Quit)
        a.triggered.connect(self.close)
        fm.addAction(a)

        # View
        vm = mb.addMenu("&View")

        def toggle(attr_name, label, checked=True):
            act = QAction(label, self, checkable=True, checked=checked)
            act.triggered.connect(lambda c, an=attr_name: (setattr(self, an, c), self._redraw()))
            vm.addAction(act)
            setattr(self, attr_name, checked)
            return act

        self._act_br     = toggle("_show_br",    "&Breathing",       True)
        self._act_hr     = toggle("_show_hr",    "&Heart Rate",      True)
        self._act_trend  = toggle("_show_trend", "HR &Trend",        True)
        self._act_btrend = toggle("_show_btrend","&Breath Trend",    True)
        self._act_sine   = toggle("_show_sine",  "&Max Excursion / Sine", True)

        vm.addSeparator()

        a = QAction("Zoom &In",  self, shortcut=QKeySequence.ZoomIn)
        a.triggered.connect(lambda: self._zoom(0.9))
        vm.addAction(a)

        a = QAction("Zoom &Out", self, shortcut=QKeySequence.ZoomOut)
        a.triggered.connect(lambda: self._zoom(1.0 / 0.9))
        vm.addAction(a)

        a = QAction("&Auto Zoom (sine window)", self)
        a.triggered.connect(self._auto_zoom)
        vm.addAction(a)

        a = QAction("Entire &Session", self)
        a.triggered.connect(self._entire_session)
        vm.addAction(a)

        vm.addSeparator()

        a = QAction("&Time Scale", self, checkable=True, checked=True)
        a.triggered.connect(lambda c: (setattr(self, "_time_scale", c), self._redraw()))
        vm.addAction(a)

        a = QAction("&Color / B&W", self)
        a.triggered.connect(self._toggle_mono)
        vm.addAction(a)

        vm.addSeparator()

        a = QAction("&Copy Image", self, shortcut=QKeySequence.Copy)
        a.triggered.connect(self._copy_image)
        vm.addAction(a)

    # ── File I/O ──────────────────────────────────────────────────────────────

    def _open_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open NeXus Export", "", "Text files (*.txt);;All files (*)"
        )
        if path:
            self._load(path)

    def _load(self, path: str):
        self.statusBar().showMessage("Processing…")
        self._drop_label.setText("Processing…")
        QApplication.processEvents()

        self._thread = QThread()
        self._worker = Worker(path)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.status.connect(self.statusBar().showMessage)
        self._worker.finished.connect(self._on_loaded)
        self._worker.finished.connect(self._thread.quit)
        self._thread.start()

    def _on_loaded(self, result):
        if isinstance(result, Exception):
            QMessageBox.critical(self, "Error", str(result))
            self._drop_label.setText(
                "Drag and drop a NeXus .txt export file here\nor use  File → Open"
            )
            self.statusBar().showMessage("Failed to load file.")
            return

        self.data = result
        self._first = 0
        self._span  = result.n_samples

        self.setWindowTitle(
            f"HRVisualizer  –  {result.name}  /  {result.resonance_bpm:.2f} bpm"
        )
        self.statusBar().showMessage(
            f"Resonance frequency: {result.resonance_bpm:.2f} bpm  |  "
            f"Avg breath amplitude: {result.br_avg:.3f}  |  "
            f"{result.n_samples // SPS // 60}:{result.n_samples // SPS % 60:02d}"
        )

        self._drop_label.setVisible(False)
        self._chart.setVisible(True)
        self._scroll.setVisible(True)

        self._set_data()
        self._entire_session()

    # ── Plot data ─────────────────────────────────────────────────────────────

    def _set_data(self):
        """Push all series data to pyqtgraph (called once after load)."""
        d = self.data

        # Breathing: full resolution but downsampled for performance
        x_br = np.arange(d.n_samples)
        self._p_br.setData(x=x_br, y=d.br,
                           downsampleMethod="peak", autoDownsample=True)

        # HR detrended: cubic spline for smooth appearance
        if len(d.rwave_time) > 3:
            try:
                cs = CubicSpline(d.rwave_time, d.rwave_val)
                x_hr = np.linspace(d.rwave_time[0], d.rwave_time[-1],
                                   (int(d.rwave_time[-1]) - int(d.rwave_time[0])) // 8)
                self._p_hr.setData(x=x_hr, y=cs(x_hr))
            except Exception:
                self._p_hr.setData(x=d.rwave_time, y=d.rwave_val)
        else:
            self._p_hr.setData(x=d.rwave_time, y=d.rwave_val)

        # HRV amplitude envelope
        self._p_trend.setData(x=d.peak_time.astype(float), y=d.rr_val)

        # Breath amplitude envelope
        self._p_btrend.setData(x=d.pbr_times.astype(float), y=d.br_val)

        # Sine fit
        self._p_sine.setData(x=d.sine_x.astype(float), y=d.sine_y)

        # Peak marker (vertical line)
        self._p_tick.setData(
            x=[d.peak_point, d.peak_point],
            y=[-YSCALE * 0.75, YSCALE],
        )

        # BPM annotation
        self._p_label.setText(f"{d.resonance_bpm:.2f}")
        self._p_label.setPos(d.peak_point, YSCALE)
        font = self._p_label.textItem.font()
        font.setPointSize(14)
        self._p_label.textItem.setFont(font)

    # ── View control ──────────────────────────────────────────────────────────

    def _set_view(self, first: int, last: int):
        if self.data is None:
            return
        n = self.data.n_samples
        first = max(0, first)
        last  = min(n - 1, last)
        if first >= last:
            return
        self._first = first
        self._span  = last - first

        self._chart.getViewBox().setXRange(first, last, padding=0)
        self._update_scroll()
        self._update_time_ticks()

    def _zoom(self, factor: float):
        if self.data is None:
            return
        center = self._first + self._span // 2
        new_span = int(self._span * factor)
        new_span = max(100, min(self.data.n_samples, new_span))
        self._set_view(center - new_span // 2, center + new_span // 2)

    def _auto_zoom(self):
        if self.data is None:
            return
        half = SINE_WIN_S * SPS // 2
        self._set_view(self.data.peak_point - half, self.data.peak_point + half)

    def _entire_session(self):
        if self.data is None:
            return
        self._set_view(0, self.data.n_samples - 1)

    def _update_scroll(self):
        self._scroll.blockSignals(True)
        self._scroll.setMinimum(0)
        self._scroll.setMaximum(max(0, self.data.n_samples - self._span))
        self._scroll.setPageStep(self._span)
        self._scroll.setSingleStep(max(1, self._span // 20))
        self._scroll.setValue(self._first)
        self._scroll.blockSignals(False)

    def _on_scroll(self, value: int):
        if self.data is None:
            return
        self._first = value
        self._chart.getViewBox().setXRange(
            self._first, self._first + self._span, padding=0
        )
        self._update_time_ticks()

    # ── Time-axis tick marks ───────────────────────────────────────────────────

    def _update_time_ticks(self):
        # Remove old ticks
        for line, label in self._tick_items:
            self._chart.removeItem(line)
            self._chart.removeItem(label)
        self._tick_items.clear()

        if not self._time_scale or self.data is None:
            return

        # Choose a nice tick interval
        chart_width  = max(self._chart.width(), 400)
        n_ticks_max  = chart_width // 100       # ~1 tick per 100 px
        duration_s   = self._span / SPS
        nice_seconds = [1, 2, 5, 10, 15, 30, 60, 120, 300]
        sec_per_tick = next(
            (s for s in nice_seconds if duration_s / s <= n_ticks_max),
            300,
        )
        spt = sec_per_tick * SPS  # samples per tick

        # Align to absolute session time
        t_start = (self._first // spt) * spt
        t = t_start
        while t <= self._first + self._span:
            if t >= self._first:
                line = self._chart.addLine(
                    x=t,
                    pen=pg.mkPen((200, 200, 200), width=1, style=Qt.DotLine),
                )
                secs   = t // SPS
                mins   = secs // 60
                secs_r = secs % 60
                label  = pg.TextItem(
                    f"{mins}:{secs_r:02d}",
                    color=(150, 150, 150),
                    anchor=(0.5, 1.0),
                )
                label.setPos(t, YSCALE * 0.95)
                self._chart.addItem(label)
                self._tick_items.append((line, label))
            t += spt

    # ── Redraw (toggle traces / colour mode) ──────────────────────────────────

    def _redraw(self):
        if self.data is None:
            return
        mono = self._monochrome

        def pen(color_c, color_m, width=2, style=Qt.SolidLine):
            c = color_m if mono else color_c
            return pg.mkPen(c, width=width, style=style)

        self._p_br.setPen(pen("b", (80, 80, 80), 2))
        self._p_br.setVisible(self._show_br)

        self._p_hr.setPen(pen("r", "k", 2))
        self._p_hr.setVisible(self._show_hr)

        self._p_trend.setPen(pen("#00cc00", (60, 60, 60), 4))
        self._p_trend.setVisible(self._show_trend)

        self._p_btrend.setPen(pen("orange", (120, 120, 120), 4, Qt.DashLine))
        self._p_btrend.setVisible(self._show_btrend)

        self._p_sine.setPen(pen((190, 190, 190), (210, 210, 210), 10))
        self._p_sine.setVisible(self._show_sine)

        self._p_tick.setVisible(self._show_sine)
        self._p_label.setVisible(self._show_sine)

        self._update_time_ticks()

    def _toggle_mono(self):
        self._monochrome = not self._monochrome
        self._redraw()

    # ── Copy image ────────────────────────────────────────────────────────────

    def _copy_image(self):
        img = self._chart.grab().toImage()
        QApplication.clipboard().setImage(img)
        self.statusBar().showMessage("Chart copied to clipboard.")

    # ── Mouse wheel → zoom ────────────────────────────────────────────────────

    def wheelEvent(self, event):
        if self.data is None:
            return
        delta = event.angleDelta().y()
        if delta < 0:
            self._zoom(0.9)
        elif delta > 0:
            self._zoom(1.0 / 0.9)
        event.accept()

    # ── Drag-and-drop ─────────────────────────────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path.endswith(".txt"):
                self._load(path)
            else:
                QMessageBox.warning(self, "HRVisualizer",
                                    "Please drop a NeXus .txt export file.")


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("HRVisualizer")

    win = HRVWindow()
    win.show()

    if len(sys.argv) > 1:
        path = sys.argv[1]
        if path.endswith(".txt"):
            win._load(path)
        else:
            QMessageBox.warning(win, "HRVisualizer",
                                f"Not a .txt file: {path}")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
