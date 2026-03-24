#!/usr/bin/env python3
"""
Convert Elite HRV + breath.cafe data → HRVisualizer format

Elite HRV exports RR intervals as simple text file (one value per line in milliseconds).
This converter creates HRVisualizer-compatible NeXus format.

Usage:
    python3 elitehrv_to_hrvisualizer.py \\
        --rr "Elite HRV 1min 30s.txt" \\
        --breath breath_schedule_20260213_203000.csv \\
        --start-time "2026-02-13T20:30:00" \\
        --output session_20260213.txt
"""

import argparse
import math
from datetime import datetime


def read_elite_hrv_rr_intervals(filepath):
    """
    Read Elite HRV RR interval file.

    Format: One RR interval per line in milliseconds
    Example:
        802
        834
        628
        ...
    """
    rr_intervals = []
    suspicious_count = 0

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and line.isdigit():
                rr_ms = int(line)
                # Keep ALL intervals - let HRVisualizer's ectopic beat removal handle artifacts
                rr_intervals.append(rr_ms)

                # Just warn about suspicious values (but keep them!)
                if rr_ms < 300 or rr_ms > 1500:
                    suspicious_count += 1

    if suspicious_count > 0:
        print(f"ℹ️  Found {suspicious_count} unusual RR intervals (will be handled by HRVisualizer)")

    return rr_intervals


def read_breath_schedule(filepath):
    """Read breath.cafe CSV export."""
    breath_schedule = []

    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Skip header
    for line in lines[1:]:
        parts = line.strip().split(',')
        if len(parts) >= 3:
            timestamp = parts[0]
            elapsed_sec = float(parts[1])
            breath_rate = float(parts[2])
            breath_schedule.append({
                'timestamp': timestamp,
                'elapsed_sec': elapsed_sec,
                'breath_rate': breath_rate
            })

    return breath_schedule


def get_breathing_rate_at_time(breath_schedule, elapsed_seconds):
    """Get breathing rate at a specific elapsed time (linear interpolation)."""
    if not breath_schedule:
        return 5.5  # Default fallback

    if elapsed_seconds <= 0:
        return breath_schedule[0]['breath_rate']

    # Find bracketing points
    for i in range(len(breath_schedule) - 1):
        if breath_schedule[i]['elapsed_sec'] <= elapsed_seconds < breath_schedule[i + 1]['elapsed_sec']:
            # Linear interpolation
            t1 = breath_schedule[i]['elapsed_sec']
            t2 = breath_schedule[i + 1]['elapsed_sec']
            r1 = breath_schedule[i]['breath_rate']
            r2 = breath_schedule[i + 1]['breath_rate']

            fraction = (elapsed_seconds - t1) / (t2 - t1) if (t2 - t1) > 0 else 0
            return r1 + (r2 - r1) * fraction

    # Past end of schedule
    return breath_schedule[-1]['breath_rate']


def generate_respiration_waveform(breath_schedule, duration_seconds, sample_rate=256):
    """Generate synthetic respiration waveform from breathing schedule."""
    num_samples = int(duration_seconds * sample_rate)

    baseline = 664.0
    amplitude = 15.0  # Matched to real NeXus data

    respiration = []
    phase = 0.0  # Track cumulative phase

    for i in range(num_samples):
        t = i / sample_rate

        # Get current breathing rate from schedule
        current_rate = get_breathing_rate_at_time(breath_schedule, t)

        # Convert to Hz
        freq_hz = current_rate / 60.0

        # Calculate phase increment for this sample
        phase_increment = 2 * math.pi * freq_hz / sample_rate

        # Generate sine wave with slight natural variation
        amp_variation = 1.0 + 0.1 * math.sin(t * 0.3)
        value = baseline + (amplitude * amp_variation * math.sin(phase))

        respiration.append(value)

        # Increment phase (this ensures smooth frequency changes)
        phase += phase_increment

    return respiration


def reconstruct_ecg_from_rr(rr_intervals, sample_rate=256):
    """
    Reconstruct ECG waveform from RR intervals.

    Creates realistic PQRST complexes at each heartbeat location.
    """
    # Calculate total samples needed
    total_duration_ms = sum(rr_intervals)
    total_duration_sec = total_duration_ms / 1000.0
    num_samples = int(total_duration_sec * sample_rate)

    # Initialize ECG array
    ecg = [16700.0] * num_samples  # High baseline to match NeXus

    # Place R-waves based on RR intervals
    current_sample = 0

    for rr_ms in rr_intervals:
        # Calculate samples until next R-wave
        samples_to_next = int((rr_ms / 1000.0) * sample_rate)

        # Place R-wave at current position
        if current_sample < num_samples:
            # Generate PQRST complex (simplified)
            # R-wave: Large negative spike
            for j in range(-3, 4):
                sample_idx = current_sample + j
                if 0 <= sample_idx < num_samples:
                    dist = abs(j)
                    if dist == 0:
                        ecg[sample_idx] = 16700.0 - 9000  # Large R-wave spike
                    else:
                        ecg[sample_idx] = 16700.0 - 9000 * (1.0 - dist / 3.0)

        current_sample += samples_to_next

    return ecg


def write_hrvisualizer_file(output_file, ecg_data, resp_data, start_time, session_name="Elite HRV Session"):
    """Write HRVisualizer-compatible NeXus format file."""

    # Parse start time
    dt = datetime.fromisoformat(start_time)

    # Calculate duration
    duration_sec = len(ecg_data) / 256

    with open(output_file, 'w') as f:
        # Write header (NeXus format)
        f.write(f"Client:\t,{session_name}\n")
        f.write(f"Session:\tEliteHRV-BreathCafe\n")
        f.write(f"Date:\t{dt.strftime('%m-%d-%Y')}\n")
        f.write(f"Time:\t{dt.strftime('%H:%M:%S')}\n")
        f.write(f"Output rate:\t256\tSamples/sec.\n")
        f.write(f"\n")
        f.write(f"Sensor\n")
        f.write(f"\n")

        # Write data (ECG, Respiration)
        for ecg, resp in zip(ecg_data, resp_data):
            f.write(f"{ecg:.3f}\t{resp:.3f}\n")

    print(f"✅ Written {len(ecg_data)} samples to {output_file}")
    print(f"   Duration: {duration_sec/60:.2f} minutes")


def main():
    parser = argparse.ArgumentParser(description='Convert Elite HRV + breath.cafe → HRVisualizer')
    parser.add_argument('--rr', required=True, help='Elite HRV RR intervals file')
    parser.add_argument('--breath', required=True, help='breath.cafe CSV schedule')
    parser.add_argument('--start-time', required=True, help='Session start time (ISO format: 2026-02-13T20:30:00)')
    parser.add_argument('--output', required=True, help='Output HRVisualizer .txt file')
    parser.add_argument('--name', default='Elite HRV Session', help='Session name')

    args = parser.parse_args()

    print("=" * 70)
    print("ELITE HRV → HRVISUALIZER CONVERTER")
    print("=" * 70)

    # Read Elite HRV RR intervals
    print(f"\n📖 Reading Elite HRV file: {args.rr}")
    rr_intervals = read_elite_hrv_rr_intervals(args.rr)
    total_duration = sum(rr_intervals) / 1000.0  # Convert to seconds
    avg_rr = sum(rr_intervals) / len(rr_intervals)
    avg_hr = 60000 / avg_rr

    print(f"✅ Loaded {len(rr_intervals)} RR intervals")
    print(f"   Duration: {total_duration:.1f} seconds ({total_duration/60:.2f} minutes)")
    print(f"   Average RR: {avg_rr:.0f} ms")
    print(f"   Average HR: {avg_hr:.1f} bpm")

    # Read breathing schedule
    print(f"\n📖 Reading breathing schedule: {args.breath}")
    breath_schedule = read_breath_schedule(args.breath)
    print(f"✅ Loaded {len(breath_schedule)} breath schedule entries")

    if breath_schedule:
        print(f"   Start rate: {breath_schedule[0]['breath_rate']:.2f} bpm")
        print(f"   End rate: {breath_schedule[-1]['breath_rate']:.2f} bpm")
        print(f"   Schedule duration: {breath_schedule[-1]['elapsed_sec']:.1f} seconds")

    # Check duration match
    schedule_duration = breath_schedule[-1]['elapsed_sec'] if breath_schedule else 0
    duration_diff = abs(total_duration - schedule_duration)

    print(f"\n⏱️  Timing check:")
    print(f"   Elite HRV duration: {total_duration:.1f} sec")
    print(f"   Breath schedule duration: {schedule_duration:.1f} sec")
    print(f"   Difference: {duration_diff:.1f} sec")

    if duration_diff > 5:
        print(f"   ⚠️  Warning: >5 second difference - check synchronization!")
    else:
        print(f"   ✅ Good synchronization")

    # Reconstruct ECG from RR intervals
    print(f"\n🫀 Reconstructing ECG from RR intervals...")
    ecg_data = reconstruct_ecg_from_rr(rr_intervals)
    print(f"✅ Generated {len(ecg_data)} ECG samples")

    # Generate respiration waveform
    print(f"\n🫁 Generating respiration waveform from breathing schedule...")
    resp_data = generate_respiration_waveform(breath_schedule, total_duration)
    print(f"✅ Generated {len(resp_data)} respiration samples")

    # Ensure equal lengths (trim to shorter)
    min_len = min(len(ecg_data), len(resp_data))
    ecg_data = ecg_data[:min_len]
    resp_data = resp_data[:min_len]

    # Write output
    print(f"\n💾 Writing HRVisualizer file: {args.output}")
    write_hrvisualizer_file(args.output, ecg_data, resp_data, args.start_time, args.name)

    print("\n" + "=" * 70)
    print("✅ CONVERSION COMPLETE!")
    print("=" * 70)
    print(f"\nNext steps:")
    print(f"1. Transfer {args.output} to Windows PC")
    print(f"2. Open HRVisualizer")
    print(f"3. Import the .txt file")
    print(f"4. View your Resonance Frequency!")
    print("=" * 70)


if __name__ == '__main__':
    main()
