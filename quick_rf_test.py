#!/usr/bin/env python3
"""
Quick RF Test - Simplified Elite HRV Converter

Assumes standard Fisher & Lehrer protocol:
- Duration: 15 minutes
- Breathing: 6.75 → 4.25 bpm
- Ratio: 1:1 (equal inhale/exhale)
- Method: Per-breath rate changes

Usage:
    python3 quick_rf_test.py "Elite HRV [timestamp].txt"

Output:
    rf_test_YYYYMMDD_HHMMSS.txt (ready for HRVisualizer)
"""

import sys
import math
from datetime import datetime
from pathlib import Path


def read_elite_hrv_rr_intervals(filepath):
    """Read Elite HRV RR interval file (one value per line in milliseconds)."""
    rr_intervals = []
    suspicious_count = 0

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and line.isdigit():
                rr_ms = int(line)
                rr_intervals.append(rr_ms)

                if rr_ms < 300 or rr_ms > 1500:
                    suspicious_count += 1

    if suspicious_count > 0:
        print(f"ℹ️  Found {suspicious_count} unusual RR intervals (HRVisualizer will handle)")

    return rr_intervals


def generate_standard_breath_schedule():
    """
    Generate standard Fisher & Lehrer breath schedule.

    Protocol:
    - 15 minutes (900 seconds)
    - 6.75 → 4.25 bpm
    - Per-breath rate changes
    - 67.04 ms period increase per breath
    """
    duration = 900  # 15 minutes in seconds
    start_rate = 6.75  # bpm
    end_rate = 4.25   # bpm

    # Calculate period changes (Fisher & Lehrer method)
    start_period_ms = (60 / start_rate) * 1000
    end_period_ms = (60 / end_rate) * 1000
    avg_period_ms = (start_period_ms + end_period_ms) / 2
    estimated_breaths = (duration * 1000) / avg_period_ms
    period_change_per_breath = (end_period_ms - start_period_ms) / estimated_breaths

    print(f"📐 Standard Fisher & Lehrer Protocol:")
    print(f"   Duration: 15 minutes")
    print(f"   Breathing: 6.75 → 4.25 bpm")
    print(f"   Period change: {period_change_per_breath:.2f} ms/breath")
    print(f"   Estimated breaths: {int(estimated_breaths)}")

    # Generate breath schedule with per-breath rate changes
    schedule = []
    breath_count = 0
    current_period_ms = start_period_ms
    elapsed_ms = 0

    # Add start point
    schedule.append({
        'elapsed_sec': 0.0,
        'breath_rate': start_rate,
        'breath_count': 0
    })

    # Generate breath-by-breath schedule
    while elapsed_ms < (duration * 1000):
        # Complete one breath
        elapsed_ms += current_period_ms
        breath_count += 1

        # Change period for next breath
        current_period_ms += period_change_per_breath

        # Convert to rate
        current_rate = 60000 / current_period_ms

        # Clamp to end rate
        if current_rate <= end_rate:
            current_rate = end_rate
            current_period_ms = (60 / end_rate) * 1000

        # Log every ~60 seconds
        if len(schedule) == 1 or (elapsed_ms / 1000) - schedule[-1]['elapsed_sec'] >= 60:
            schedule.append({
                'elapsed_sec': elapsed_ms / 1000,
                'breath_rate': current_rate,
                'breath_count': breath_count
            })

    # Add final point at exactly 15 minutes
    schedule.append({
        'elapsed_sec': 900.0,
        'breath_rate': end_rate,
        'breath_count': breath_count
    })

    return schedule


def get_breathing_rate_at_time(breath_schedule, elapsed_seconds):
    """Get breathing rate at a specific time (linear interpolation)."""
    if elapsed_seconds <= 0:
        return breath_schedule[0]['breath_rate']

    for i in range(len(breath_schedule) - 1):
        if breath_schedule[i]['elapsed_sec'] <= elapsed_seconds < breath_schedule[i + 1]['elapsed_sec']:
            t1 = breath_schedule[i]['elapsed_sec']
            t2 = breath_schedule[i + 1]['elapsed_sec']
            r1 = breath_schedule[i]['breath_rate']
            r2 = breath_schedule[i + 1]['breath_rate']

            fraction = (elapsed_seconds - t1) / (t2 - t1) if (t2 - t1) > 0 else 0
            return r1 + (r2 - r1) * fraction

    return breath_schedule[-1]['breath_rate']


def generate_respiration_waveform(breath_schedule, duration_seconds, sample_rate=256):
    """Generate synthetic respiration waveform from breathing schedule."""
    num_samples = int(duration_seconds * sample_rate)
    baseline = 664.0
    amplitude = 15.0
    respiration = []
    phase = 0.0

    for i in range(num_samples):
        t = i / sample_rate
        current_rate = get_breathing_rate_at_time(breath_schedule, t)
        freq_hz = current_rate / 60.0
        phase_increment = 2 * math.pi * freq_hz / sample_rate

        amp_variation = 1.0 + 0.1 * math.sin(t * 0.3)
        value = baseline + (amplitude * amp_variation * math.sin(phase))

        respiration.append(value)
        phase += phase_increment

    return respiration


def reconstruct_ecg_from_rr(rr_intervals, sample_rate=256):
    """Reconstruct ECG waveform from RR intervals."""
    total_duration_ms = sum(rr_intervals)
    total_duration_sec = total_duration_ms / 1000.0
    num_samples = int(total_duration_sec * sample_rate)

    ecg = [16700.0] * num_samples
    current_sample = 0

    for rr_ms in rr_intervals:
        samples_to_next = int((rr_ms / 1000.0) * sample_rate)

        if current_sample < num_samples:
            for j in range(-3, 4):
                sample_idx = current_sample + j
                if 0 <= sample_idx < num_samples:
                    dist = abs(j)
                    if dist == 0:
                        ecg[sample_idx] = 16700.0 - 9000
                    else:
                        ecg[sample_idx] = 16700.0 - 9000 * (1.0 - dist / 3.0)

        current_sample += samples_to_next

    return ecg


def write_hrvisualizer_file(output_file, ecg_data, resp_data, session_name="RF Test"):
    """Write HRVisualizer-compatible file."""
    now = datetime.now()
    duration_sec = len(ecg_data) / 256

    with open(output_file, 'w') as f:
        f.write(f"Client:\t,{session_name}\n")
        f.write(f"Session:\tFisher-Lehrer-RF-Test\n")
        f.write(f"Date:\t{now.strftime('%m-%d-%Y')}\n")
        f.write(f"Time:\t{now.strftime('%H:%M:%S')}\n")
        f.write(f"Output rate:\t256\tSamples/sec.\n")
        f.write(f"\n")
        f.write(f"Sensor\n")
        f.write(f"\n")

        for ecg, resp in zip(ecg_data, resp_data):
            f.write(f"{ecg:.3f}\t{resp:.3f}\n")

    print(f"✅ Written {len(ecg_data)} samples ({duration_sec/60:.2f} minutes)")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 quick_rf_test.py <elite_hrv_file.txt>")
        print("\nExample:")
        print('  python3 quick_rf_test.py "Elite HRV 20260213_194147.txt"')
        sys.exit(1)

    elite_hrv_file = sys.argv[1]

    if not Path(elite_hrv_file).exists():
        print(f"❌ File not found: {elite_hrv_file}")
        sys.exit(1)

    print("=" * 70)
    print("QUICK RF TEST - Standard Fisher & Lehrer Protocol")
    print("=" * 70)

    # Read Elite HRV data
    print(f"\n📖 Reading Elite HRV file: {elite_hrv_file}")
    rr_intervals = read_elite_hrv_rr_intervals(elite_hrv_file)
    total_duration = sum(rr_intervals) / 1000.0
    avg_rr = sum(rr_intervals) / len(rr_intervals)
    avg_hr = 60000 / avg_rr

    print(f"✅ Loaded {len(rr_intervals)} RR intervals")
    print(f"   Duration: {total_duration:.1f} seconds ({total_duration/60:.2f} minutes)")
    print(f"   Average HR: {avg_hr:.1f} bpm")

    # Generate standard breath schedule
    print(f"\n🫁 Generating standard Fisher & Lehrer breath schedule...")
    breath_schedule = generate_standard_breath_schedule()

    # Check timing
    schedule_duration = 900.0  # Always 15 minutes
    duration_diff = abs(total_duration - schedule_duration)
    print(f"\n⏱️  Timing check:")
    print(f"   Elite HRV: {total_duration:.1f} sec")
    print(f"   Protocol: {schedule_duration:.1f} sec")
    print(f"   Difference: {duration_diff:.1f} sec")
    if duration_diff > 30:
        print(f"   ⚠️  Warning: Session may have started/stopped early")

    # Reconstruct ECG
    print(f"\n🫀 Reconstructing ECG from RR intervals...")
    ecg_data = reconstruct_ecg_from_rr(rr_intervals)

    # Generate respiration
    print(f"\n🫁 Generating synthetic respiration waveform...")
    resp_data = generate_respiration_waveform(breath_schedule, total_duration)

    # Ensure equal lengths
    min_len = min(len(ecg_data), len(resp_data))
    ecg_data = ecg_data[:min_len]
    resp_data = resp_data[:min_len]

    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"rf_test_{timestamp}.txt"

    # Write output
    print(f"\n💾 Writing HRVisualizer file: {output_file}")
    write_hrvisualizer_file(output_file, ecg_data, resp_data, f"RF Test {timestamp}")

    print("\n" + "=" * 70)
    print("✅ CONVERSION COMPLETE!")
    print("=" * 70)
    print(f"\n📁 Output file: {output_file}")
    print(f"\n🎯 Next steps:")
    print(f"   1. Transfer {output_file} to Windows PC")
    print(f"   2. Open HRVisualizer")
    print(f"   3. Import the file")
    print(f"   4. Your RF will be displayed!")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
