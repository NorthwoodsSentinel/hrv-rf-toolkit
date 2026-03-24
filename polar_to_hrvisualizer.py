#!/usr/bin/env python3
"""
Polar H10 to HRVisualizer Converter
====================================

Converts Polar H10 RR interval data + breathing schedule to HRVisualizer format.

Usage:
    python polar_to_hrvisualizer.py \
        --rr RR_20260213_143000.csv \
        --breath breath_schedule_20260213_143000.csv \
        --output hrv_session_20260213_143000.txt

Author: Generated for HRVisualizer adaptation project
Date: 2026-02-13
"""

import argparse
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Optional
import math


class PolarToHRVisualizer:
    """Converts Polar H10 data to HRVisualizer format."""

    # Constants matching HRVisualizer expectations
    SAMPLE_RATE = 256  # Hz - samples per second
    RESP_EFFECTIVE_RATE = 32  # Hz - effective respiration sampling rate
    RESP_DECIMATION = 8  # Store every 8th sample for respiration

    def __init__(self, rr_file: Path, breath_file: Path, output_file: Path):
        """Initialize converter with file paths."""
        self.rr_file = Path(rr_file)
        self.breath_file = Path(breath_file)
        self.output_file = Path(output_file)

        self.rr_intervals = []  # RR intervals in milliseconds
        self.rr_timestamps = []  # Absolute timestamps for each RR interval
        self.breath_schedule = []  # List of (timestamp, breath_rate_bpm) tuples

        self.session_start = None
        self.session_duration = 0  # seconds
        self.total_samples = 0

    def parse_rr_intervals(self) -> None:
        """Parse Polar RR interval file (CSV or TXT format)."""
        print(f"📖 Reading RR intervals from: {self.rr_file}")

        with open(self.rr_file, 'r') as f:
            # Try to detect format
            first_line = f.readline().strip()
            f.seek(0)  # Reset to beginning

            if ',' in first_line or 'Timestamp' in first_line:
                # CSV format (EphorPolar or ECG Recorder with timestamps)
                reader = csv.DictReader(f)

                for row in reader:
                    # Try different column name variations
                    rr_ms = None
                    timestamp = None

                    # Common RR interval column names
                    for key in ['RR_Interval', 'RR_Interval_ms', 'RR', 'rr_interval']:
                        if key in row:
                            rr_ms = float(row[key])
                            break

                    # Common timestamp column names
                    for key in ['Timestamp', 'timestamp', 'Time', 'time']:
                        if key in row:
                            timestamp = row[key]
                            break

                    if rr_ms is not None:
                        self.rr_intervals.append(rr_ms)
                        if timestamp:
                            self.rr_timestamps.append(self._parse_timestamp(timestamp))

            else:
                # Plain text format (one RR interval per line in milliseconds)
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            rr_ms = float(line)
                            self.rr_intervals.append(rr_ms)
                        except ValueError:
                            continue

        if not self.rr_intervals:
            raise ValueError("No RR intervals found in file!")

        print(f"✅ Loaded {len(self.rr_intervals)} RR intervals")
        print(f"   Range: {min(self.rr_intervals):.1f} - {max(self.rr_intervals):.1f} ms")
        print(f"   Mean: {sum(self.rr_intervals)/len(self.rr_intervals):.1f} ms "
              f"(~{60000/sum(self.rr_intervals)*len(self.rr_intervals):.1f} bpm)")

    def parse_breath_schedule(self) -> None:
        """Parse breathing schedule CSV from breath.cafe."""
        print(f"\n📖 Reading breathing schedule from: {self.breath_file}")

        with open(self.breath_file, 'r') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Try different column name variations
                timestamp = None
                elapsed = None
                breath_rate = None

                # Timestamp
                for key in ['Timestamp', 'timestamp', 'Absolute_Time', 'Clock_Time']:
                    if key in row and row[key]:
                        timestamp = row[key]
                        break

                # Elapsed seconds (alternative to timestamp)
                for key in ['Elapsed_Seconds', 'elapsed', 'Elapsed', 'Time']:
                    if key in row and row[key]:
                        try:
                            elapsed = float(row[key])
                        except ValueError:
                            pass
                        break

                # Breathing rate
                for key in ['Breath_Rate_BPM', 'breath_rate', 'Rate', 'bpm', 'BreathRate']:
                    if key in row and row[key]:
                        try:
                            breath_rate = float(row[key])
                        except ValueError:
                            pass
                        break

                if breath_rate is not None:
                    if timestamp:
                        parsed_time = self._parse_timestamp(timestamp)
                        self.breath_schedule.append((parsed_time, breath_rate))
                    elif elapsed is not None:
                        self.breath_schedule.append((elapsed, breath_rate))

        if not self.breath_schedule:
            raise ValueError("No breathing schedule found in file!")

        print(f"✅ Loaded {len(self.breath_schedule)} breathing rate changes")
        print(f"   Rate range: {min(r for _, r in self.breath_schedule):.2f} - "
              f"{max(r for _, r in self.breath_schedule):.2f} bpm")

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string in various formats."""
        # Try different timestamp formats
        formats = [
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S',
            '%H:%M:%S.%f',
            '%H:%M:%S',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Could not parse timestamp: {timestamp_str}")

    def align_timestamps(self) -> None:
        """Align RR timestamps with breathing schedule."""
        print(f"\n⏱️  Aligning timestamps...")

        # Determine session start time
        if self.rr_timestamps:
            self.session_start = self.rr_timestamps[0]
            print(f"   Session start: {self.session_start}")
        elif isinstance(self.breath_schedule[0][0], datetime):
            self.session_start = self.breath_schedule[0][0]
            print(f"   Session start (from breathing): {self.session_start}")
        else:
            # No absolute timestamps, use relative timing
            self.session_start = datetime.now()
            print(f"   Using relative timing (no absolute timestamps)")

        # If RR intervals don't have timestamps, generate them from intervals
        if not self.rr_timestamps:
            cumulative_time = 0
            for rr_ms in self.rr_intervals:
                timestamp = self.session_start + timedelta(milliseconds=cumulative_time)
                self.rr_timestamps.append(timestamp)
                cumulative_time += rr_ms

        # Convert breath schedule to absolute times if needed
        if self.breath_schedule and isinstance(self.breath_schedule[0][0], (int, float)):
            # Convert elapsed seconds to absolute timestamps
            new_schedule = []
            for elapsed_sec, breath_rate in self.breath_schedule:
                timestamp = self.session_start + timedelta(seconds=elapsed_sec)
                new_schedule.append((timestamp, breath_rate))
            self.breath_schedule = new_schedule

        # Calculate session duration
        if self.rr_timestamps:
            last_rr_time = self.rr_timestamps[-1]
            self.session_duration = (last_rr_time - self.session_start).total_seconds()
            self.total_samples = int(self.session_duration * self.SAMPLE_RATE)

            print(f"   Session duration: {self.session_duration:.1f} seconds ({self.session_duration/60:.1f} minutes)")
            print(f"   Total samples: {self.total_samples} (at {self.SAMPLE_RATE} Hz)")

    def generate_synthetic_respiration(self) -> List[float]:
        """Generate synthetic respiration waveform from breathing schedule."""
        print(f"\n🫁 Generating synthetic respiration waveform...")

        # Initialize respiration array
        respiration = [0.0] * self.total_samples

        # Baseline value for respiration (match real HRVisualizer data scale)
        baseline = 664.0
        amplitude = 15.0  # Small amplitude to match real data (±15 units)

        # Generate respiration for each sample
        for sample_idx in range(self.total_samples):
            # Calculate time for this sample
            sample_time = self.session_start + timedelta(seconds=sample_idx / self.SAMPLE_RATE)

            # Find applicable breathing rate
            breath_rate_bpm = self._get_breath_rate_at_time(sample_time)

            # Convert to Hz
            breath_freq_hz = breath_rate_bpm / 60.0

            # Time in seconds
            t = sample_idx / self.SAMPLE_RATE

            # Generate sine wave with natural variation
            # Add slight amplitude modulation (±10%) for realism
            amplitude_variation = 1.0 + 0.1 * math.sin(t * 0.3)

            # Add slight frequency modulation (±2%) for realism
            freq_variation = 1.0 + 0.02 * math.sin(t * 0.5)

            # Sine wave: baseline + amplitude * sin(2π * frequency * time)
            value = baseline + (amplitude * amplitude_variation *
                              math.sin(2 * math.pi * breath_freq_hz * freq_variation * t))

            respiration[sample_idx] = value

        print(f"✅ Generated {len(respiration)} respiration samples")
        print(f"   Range: {min(respiration):.1f} - {max(respiration):.1f} (arbitrary units)")

        return respiration

    def _get_breath_rate_at_time(self, time: datetime) -> float:
        """Get breathing rate at specific time (interpolated)."""
        # Find the two breath schedule points surrounding this time
        before = None
        after = None

        for i, (timestamp, rate) in enumerate(self.breath_schedule):
            if timestamp <= time:
                before = (timestamp, rate)
            elif timestamp > time:
                after = (timestamp, rate)
                break

        # If before start, use first rate
        if before is None:
            return self.breath_schedule[0][1]

        # If after end, use last rate
        if after is None:
            return self.breath_schedule[-1][1]

        # Linear interpolation between rates
        time_before, rate_before = before
        time_after, rate_after = after

        total_duration = (time_after - time_before).total_seconds()
        elapsed = (time - time_before).total_seconds()

        if total_duration == 0:
            return rate_before

        fraction = elapsed / total_duration
        interpolated_rate = rate_before + (rate_after - rate_before) * fraction

        return interpolated_rate

    def reconstruct_ecg_from_rr(self) -> List[float]:
        """Reconstruct ECG-like signal from RR intervals."""
        print(f"\n💓 Reconstructing ECG from RR intervals...")

        # Initialize ECG array with baseline (match real HRVisualizer data scale)
        baseline = 16700.0  # High baseline to match real data
        ecg = [baseline] * self.total_samples

        # Collect R-wave sample positions first
        r_wave_positions = []
        cumulative_time_ms = 0

        for rr_ms in self.rr_intervals:
            sample_position = int((cumulative_time_ms / 1000.0) * self.SAMPLE_RATE)
            if 0 <= sample_position < self.total_samples:
                r_wave_positions.append(sample_position)
            cumulative_time_ms += rr_ms

        print(f"✅ Found {len(r_wave_positions)} R-wave positions")

        # Generate ECG waveform for each beat
        for i in range(len(r_wave_positions)):
            r_pos = r_wave_positions[i]

            # Determine interval to next R-wave
            if i < len(r_wave_positions) - 1:
                next_r_pos = r_wave_positions[i + 1]
                rr_samples = next_r_pos - r_pos
            else:
                # Last R-wave - use previous interval
                if i > 0:
                    rr_samples = r_wave_positions[i] - r_wave_positions[i - 1]
                else:
                    rr_samples = int(1.0 * self.SAMPLE_RATE)

            # Generate PQRST complex (simplified)
            # All positions relative to R-wave

            # P wave: 60-30 samples before R (small positive deflection)
            p_start = max(0, r_pos - 60)
            p_peak = max(0, r_pos - 45)
            p_end = max(0, r_pos - 30)

            for j in range(p_start, p_peak):
                if j < self.total_samples:
                    phase = (j - p_start) / max(1, p_peak - p_start)
                    ecg[j] = baseline + 200 * math.sin(math.pi * phase)

            for j in range(p_peak, p_end):
                if j < self.total_samples:
                    phase = (j - p_peak) / max(1, p_end - p_peak)
                    ecg[j] = baseline + 200 * math.sin(math.pi + math.pi * phase)

            # QRS complex: sharp spike
            # Q wave: small negative deflection
            for j in range(max(0, r_pos - 8), r_pos - 2):
                if j < self.total_samples:
                    ecg[j] = baseline - 1000

            # R wave: large negative spike (THE PEAK - inverted in real data!)
            for j in range(max(0, r_pos - 2), min(self.total_samples, r_pos + 3)):
                if j < self.total_samples:
                    dist = abs(j - r_pos)
                    ecg[j] = baseline - 9000 * (1.0 - dist / 3.0)  # Large negative spike

            # S wave: return to baseline after R
            for j in range(r_pos + 3, min(self.total_samples, r_pos + 10)):
                if j < self.total_samples:
                    ecg[j] = baseline - 500

            # T wave: broader positive deflection at ~40% into RR interval
            t_center = min(self.total_samples - 1, r_pos + int(rr_samples * 0.35))
            t_width = int(rr_samples * 0.15)
            t_start = max(0, t_center - t_width // 2)
            t_end = min(self.total_samples, t_center + t_width // 2)

            for j in range(t_start, t_end):
                if j < self.total_samples:
                    phase = (j - t_start) / max(1, t_end - t_start)
                    ecg[j] = baseline + 400 * math.sin(math.pi * phase)

            # Ensure baseline between beats (after T wave until next P wave)
            baseline_start = min(self.total_samples, t_end + 10)
            baseline_end = min(self.total_samples, r_pos + int(rr_samples * 0.9))
            for j in range(baseline_start, baseline_end):
                if j < self.total_samples:
                    ecg[j] = baseline

        print(f"✅ Generated ECG waveform with {len(r_wave_positions)} beats")

        return ecg

    def write_hrvisualizer_format(self, ecg: List[float], respiration: List[float]) -> None:
        """Write data in HRVisualizer format."""
        print(f"\n📝 Writing HRVisualizer format to: {self.output_file}")

        # Create output directory if needed
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_file, 'w') as f:
            # Write header
            f.write(f"Client:     Polar_H10_User\n")
            f.write(f"Session:    Converted_Session\n")
            f.write(f"Date:       {self.session_start.strftime('%m-%d-%Y')}\n")
            f.write(f"Time:       {self.session_start.strftime('%H:%M:%S')}\n")
            f.write(f"Duration:   {int(self.session_duration)} Seconds\n")
            f.write(f"Output rate: {self.SAMPLE_RATE} Samples/sec\n")
            f.write(f"{self.SAMPLE_RATE} SPS\t{self.RESP_EFFECTIVE_RATE} SPS\n")
            f.write(f"Sensor-B:ECG/EKG\tSensor-G:RSP\n")
            f.write(f"\n")

            # Write data columns
            # Column 1: ECG (256 Hz)
            # Column 2: Respiration (256 Hz storage, 32 Hz effective via 8:1 decimation)
            for i in range(min(len(ecg), len(respiration))):
                f.write(f"{ecg[i]:.1f}\t{respiration[i]:.1f}\n")

        print(f"✅ Wrote {min(len(ecg), len(respiration))} samples")
        print(f"   File size: {self.output_file.stat().st_size / 1024:.1f} KB")

    def convert(self) -> None:
        """Run the complete conversion process."""
        print("=" * 60)
        print("POLAR H10 TO HRVISUALIZER CONVERTER")
        print("=" * 60)

        try:
            # Step 1: Parse input files
            self.parse_rr_intervals()
            self.parse_breath_schedule()

            # Step 2: Align timestamps
            self.align_timestamps()

            # Step 3: Generate synthetic respiration
            respiration = self.generate_synthetic_respiration()

            # Step 4: Reconstruct ECG from RR intervals
            ecg = self.reconstruct_ecg_from_rr()

            # Step 5: Write output
            self.write_hrvisualizer_format(ecg, respiration)

            print("\n" + "=" * 60)
            print("✅ CONVERSION COMPLETE!")
            print("=" * 60)
            print(f"\n📂 Output file: {self.output_file}")
            print(f"\nNext step: Import {self.output_file.name} into HRVisualizer")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Convert Polar H10 RR intervals to HRVisualizer format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert real Polar H10 data
  python polar_to_hrvisualizer.py \\
      --rr RR_20260213_143000.csv \\
      --breath breath_schedule_20260213_143000.csv \\
      --output hrv_session_20260213_143000.txt

  # Convert test data
  python polar_to_hrvisualizer.py \\
      --rr test_data/test_rr_intervals.csv \\
      --breath test_data/test_breath_schedule.csv \\
      --output test_data/test_output.txt
        """
    )

    parser.add_argument('--rr', required=True, type=Path,
                       help='Path to Polar RR interval file (CSV or TXT)')
    parser.add_argument('--breath', required=True, type=Path,
                       help='Path to breathing schedule CSV file')
    parser.add_argument('--output', required=True, type=Path,
                       help='Path for output HRVisualizer file (.txt)')

    args = parser.parse_args()

    # Validate input files exist
    if not args.rr.exists():
        print(f"❌ Error: RR interval file not found: {args.rr}")
        sys.exit(1)

    if not args.breath.exists():
        print(f"❌ Error: Breathing schedule file not found: {args.breath}")
        sys.exit(1)

    # Run conversion
    converter = PolarToHRVisualizer(args.rr, args.breath, args.output)
    converter.convert()


if __name__ == '__main__':
    main()
