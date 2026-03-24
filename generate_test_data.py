#!/usr/bin/env python3
"""
Generate Realistic Test Data for Polar H10 Converter
=====================================================

Creates synthetic but realistic:
1. Polar H10 RR interval data (with RSA pattern)
2. Breathing schedule (matching breath.cafe format)

This allows testing the converter before Polar H10 hardware arrives.

Usage:
    python generate_test_data.py --output test_data/

Author: Generated for HRVisualizer testing
Date: 2026-02-13
"""

import argparse
import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path


class TestDataGenerator:
    """Generate realistic synthetic HRV data."""

    def __init__(self, output_dir: Path, duration_minutes: float = 15):
        """Initialize generator."""
        self.output_dir = Path(output_dir)
        self.duration_minutes = duration_minutes
        self.duration_seconds = duration_minutes * 60

        # Session timing
        self.session_start = datetime(2026, 2, 13, 14, 30, 0)

        # Breathing protocol (Fisher & Lehrer sliding method)
        self.breath_rate_start = 6.75  # bpm
        self.breath_rate_end = 4.25    # bpm

        # Physiological parameters
        self.base_hr = 72  # bpm (resting heart rate)
        self.rsa_amplitude = 15  # bpm (respiratory sinus arrhythmia amplitude)

        # Resonance frequency (simulated true RF for this "person")
        self.true_rf = 5.5  # bpm - should be detected by HRVisualizer

    def generate_rr_intervals(self) -> list:
        """Generate realistic RR intervals with RSA."""
        print(f"💓 Generating RR intervals with respiratory sinus arrhythmia...")

        rr_intervals = []
        timestamps = []
        current_time = self.session_start

        elapsed_sec = 0
        while elapsed_sec < self.duration_seconds:
            # Current breathing rate (linear interpolation)
            breath_rate = self._get_breath_rate_at_time(elapsed_sec)

            # Calculate RSA effect
            # RSA amplitude peaks near true RF
            rf_proximity = 1.0 - abs(breath_rate - self.true_rf) / 3.0
            rf_proximity = max(0.3, min(1.0, rf_proximity))  # Clamp 0.3-1.0

            # RSA modulation (HR increases on inhale, decreases on exhale)
            breath_phase = (elapsed_sec % (60 / breath_rate)) / (60 / breath_rate)
            rsa_effect = self.rsa_amplitude * rf_proximity * math.sin(breath_phase * 2 * math.pi)

            # Instantaneous heart rate
            hr = self.base_hr + rsa_effect

            # Add small random variation (natural variability)
            hr += random.gauss(0, 2)

            # Convert HR to RR interval (milliseconds)
            rr_ms = 60000.0 / hr

            # Add small measurement noise (±2 ms)
            rr_ms += random.gauss(0, 2)

            # Ensure physiological range (400-1500 ms = 40-150 bpm)
            rr_ms = max(400, min(1500, rr_ms))

            rr_intervals.append(rr_ms)
            timestamps.append(current_time)

            # Advance time
            current_time += timedelta(milliseconds=rr_ms)
            elapsed_sec += rr_ms / 1000.0

        print(f"✅ Generated {len(rr_intervals)} RR intervals")
        print(f"   Duration: {elapsed_sec:.1f} seconds")
        print(f"   Mean RR: {sum(rr_intervals)/len(rr_intervals):.1f} ms")
        print(f"   Mean HR: {60000/(sum(rr_intervals)/len(rr_intervals)):.1f} bpm")
        print(f"   HRV (SDNN): {self._calculate_sdnn(rr_intervals):.1f} ms")

        return rr_intervals, timestamps

    def generate_breath_schedule(self) -> list:
        """Generate breathing schedule matching breath.cafe format."""
        print(f"\n🫁 Generating breathing schedule...")

        schedule = []

        # Log every 60 seconds (matching breath.cafe auto-log)
        for elapsed_sec in range(0, int(self.duration_seconds) + 1, 60):
            timestamp = self.session_start + timedelta(seconds=elapsed_sec)
            breath_rate = self._get_breath_rate_at_time(elapsed_sec)

            # Determine event type
            if elapsed_sec == 0:
                event_type = 'START'
            elif elapsed_sec >= self.duration_seconds:
                event_type = 'END'
            else:
                event_type = 'AUTO'

            schedule.append({
                'timestamp': timestamp,
                'elapsed': elapsed_sec,
                'breath_rate': breath_rate,
                'event_type': event_type
            })

        print(f"✅ Generated {len(schedule)} breath schedule entries")
        print(f"   Rate range: {self.breath_rate_start} → {self.breath_rate_end} bpm")

        return schedule

    def _get_breath_rate_at_time(self, elapsed_sec: float) -> float:
        """Calculate breathing rate at given time (linear interpolation)."""
        rate_change_per_sec = (self.breath_rate_end - self.breath_rate_start) / self.duration_seconds
        breath_rate = self.breath_rate_start + (rate_change_per_sec * elapsed_sec)
        return breath_rate

    def _calculate_sdnn(self, rr_intervals: list) -> float:
        """Calculate SDNN (standard deviation of RR intervals)."""
        if len(rr_intervals) < 2:
            return 0.0
        mean = sum(rr_intervals) / len(rr_intervals)
        variance = sum((rr - mean) ** 2 for rr in rr_intervals) / len(rr_intervals)
        return math.sqrt(variance)

    def save_rr_intervals_ephorpolar_format(self, rr_intervals: list, timestamps: list) -> Path:
        """Save RR intervals in EphorPolar CSV format."""
        output_file = self.output_dir / 'test_rr_intervals.csv'

        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'RR_Interval'])

            for timestamp, rr_ms in zip(timestamps, rr_intervals):
                timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # milliseconds
                writer.writerow([timestamp_str, f'{rr_ms:.1f}'])

        print(f"\n💾 Saved RR intervals: {output_file}")
        return output_file

    def save_rr_intervals_txt_format(self, rr_intervals: list) -> Path:
        """Save RR intervals in plain text format (one per line)."""
        output_file = self.output_dir / 'test_rr_intervals.txt'

        with open(output_file, 'w') as f:
            for rr_ms in rr_intervals:
                f.write(f'{rr_ms:.1f}\n')

        print(f"💾 Saved RR intervals (TXT): {output_file}")
        return output_file

    def save_breath_schedule(self, schedule: list) -> Path:
        """Save breathing schedule in breath.cafe format."""
        output_file = self.output_dir / 'test_breath_schedule.csv'

        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Elapsed_Seconds', 'Breath_Rate_BPM', 'Event_Type'])

            for entry in schedule:
                timestamp_str = entry['timestamp'].isoformat() + 'Z'
                writer.writerow([
                    timestamp_str,
                    f"{entry['elapsed']:.3f}",
                    f"{entry['breath_rate']:.2f}",
                    entry['event_type']
                ])

        print(f"💾 Saved breath schedule: {output_file}")
        return output_file

    def generate_readme(self) -> None:
        """Generate README explaining test data."""
        readme_file = self.output_dir / 'README_TEST_DATA.md'

        content = f"""# Test Data for Polar H10 to HRVisualizer Converter

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This directory contains synthetic test data simulating a real Polar H10 + breath.cafe session.

## Test Data Characteristics

### Session Parameters
- **Duration:** {self.duration_minutes} minutes ({self.duration_seconds} seconds)
- **Start Time:** {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}
- **Breathing Protocol:** Sliding {self.breath_rate_start} → {self.breath_rate_end} bpm

### Simulated Physiology
- **Base Heart Rate:** {self.base_hr} bpm
- **RSA Amplitude:** {self.rsa_amplitude} bpm (peak-to-peak)
- **True RF (simulated):** {self.true_rf} bpm
  - HRVisualizer should detect RF near this value!

### Respiratory Sinus Arrhythmia (RSA)
The synthetic data includes realistic RSA:
- HR increases during inhalation (vagal withdrawal)
- HR decreases during exhalation (vagal activation)
- RSA amplitude peaks when breathing near RF ({self.true_rf} bpm)
- RSA amplitude decreases when breathing far from RF

## Files

### 1. `test_rr_intervals.csv`
**Format:** EphorPolar CSV export format
```csv
Timestamp,RR_Interval
2026-02-13 14:30:00.000,820.5
2026-02-13 14:30:00.820,835.2
...
```

### 2. `test_rr_intervals.txt`
**Format:** Plain text (one RR interval per line in milliseconds)
```
820.5
835.2
810.3
...
```

### 3. `test_breath_schedule.csv`
**Format:** breath.cafe export format
```csv
Timestamp,Elapsed_Seconds,Breath_Rate_BPM,Event_Type
2026-02-13T14:30:00.000Z,0.000,6.75,START
2026-02-13T14:31:00.015Z,60.015,6.58,AUTO
...
```

## Testing the Converter

Run the converter with test data:

```bash
python polar_to_hrvisualizer.py \\
    --rr test_data/test_rr_intervals.csv \\
    --breath test_data/test_breath_schedule.csv \\
    --output test_data/test_output.txt
```

## Expected Results

When importing `test_output.txt` into HRVisualizer:

### ✅ Success Criteria
- **RF Detection:** Should detect RF near {self.true_rf} bpm (±0.3 bpm acceptable)
- **Max HRV Window:** Should occur around minute 7-8 (when breathing closest to {self.true_rf} bpm)
- **Visual Display:** HR and respiration should show clear phase relationship

### 📊 Why {self.true_rf} bpm?
The test data is generated with maximum RSA amplitude at {self.true_rf} bpm.
This simulates a person whose true resonance frequency is {self.true_rf} bpm.

As breathing rate passes through {self.true_rf} bpm during the sliding protocol:
- Minute 0-7: Approaching RF (increasing HRV amplitude)
- Minute 7-8: At or near RF (maximum HRV amplitude) ← Peak detected here
- Minute 8-15: Moving away from RF (decreasing HRV amplitude)

### 🔍 Validation Checks

1. **Open HRVisualizer display:**
   - Look for 1-minute window marked as max HRV
   - Should be around timestamp 7-8 minutes into session

2. **Check detected RF:**
   - Should report RF ≈ {self.true_rf} bpm
   - Within 0.3-0.5 bpm is excellent
   - Within 0.5-1.0 bpm is acceptable

3. **Visual inspection:**
   - HR oscillations should be largest in middle of session
   - HR and respiration should be in phase (HR↑ on inhale)

## Troubleshooting

### RF detected is way off (>1 bpm error)
- Likely respiration waveform generation issue
- Check synthetic respiration amplitude/frequency
- Verify breath schedule timestamps align with RR timestamps

### No clear HRV peak
- Check if session duration is sufficient
- Verify RSA amplitude is realistic (10-20 bpm typical)
- Ensure breathing rate passes through RF

### Phase relationship inverted
- Timing synchronization error
- RR intervals and breath schedule may be offset
- Check timestamp alignment in converter

## Next Steps

Once test data conversion succeeds:
1. ✅ Converter works end-to-end
2. ✅ HRVisualizer can import the file
3. ✅ RF detection produces reasonable results
4. → Ready for real Polar H10 data!

## Generating New Test Data

To regenerate with different parameters:

```bash
python generate_test_data.py \\
    --output test_data/ \\
    --duration 15 \\
    --base-hr 72 \\
    --true-rf 5.5
```

See `python generate_test_data.py --help` for all options.
"""

        with open(readme_file, 'w') as f:
            f.write(content)

        print(f"📄 Generated README: {readme_file}")

    def generate(self) -> None:
        """Generate all test data files."""
        print("=" * 60)
        print("TEST DATA GENERATOR FOR POLAR H10 CONVERTER")
        print("=" * 60)
        print(f"Session: {self.duration_minutes} min, RF={self.true_rf} bpm")
        print("=" * 60)

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate data
        rr_intervals, timestamps = self.generate_rr_intervals()
        breath_schedule = self.generate_breath_schedule()

        # Save in multiple formats
        self.save_rr_intervals_ephorpolar_format(rr_intervals, timestamps)
        self.save_rr_intervals_txt_format(rr_intervals)
        self.save_breath_schedule(breath_schedule)

        # Generate documentation
        self.generate_readme()

        print("\n" + "=" * 60)
        print("✅ TEST DATA GENERATION COMPLETE!")
        print("=" * 60)
        print(f"\n📂 Output directory: {self.output_dir.absolute()}")
        print("\nNext step: Run the converter:")
        print(f"\n  python polar_to_hrvisualizer.py \\")
        print(f"      --rr {self.output_dir}/test_rr_intervals.csv \\")
        print(f"      --breath {self.output_dir}/test_breath_schedule.csv \\")
        print(f"      --output {self.output_dir}/test_output.txt")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Generate realistic test data for Polar H10 converter',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--output', type=Path, default='test_data',
                       help='Output directory for test data (default: test_data/)')
    parser.add_argument('--duration', type=float, default=15,
                       help='Session duration in minutes (default: 15)')
    parser.add_argument('--base-hr', type=float, default=72,
                       help='Base heart rate in bpm (default: 72)')
    parser.add_argument('--true-rf', type=float, default=5.5,
                       help='Simulated true RF in bpm (default: 5.5)')

    args = parser.parse_args()

    # Create generator
    generator = TestDataGenerator(
        output_dir=args.output,
        duration_minutes=args.duration
    )

    # Override defaults if specified
    if args.base_hr != 72:
        generator.base_hr = args.base_hr
    if args.true_rf != 5.5:
        generator.true_rf = args.true_rf

    # Generate test data
    generator.generate()


if __name__ == '__main__':
    main()
