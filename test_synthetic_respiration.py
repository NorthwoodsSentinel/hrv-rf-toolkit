#!/usr/bin/env python3
"""
Test Impact of Synthetic Respiration on RF Detection
=====================================================

Compares:
1. Original Alyssa.txt (real respiration waveform)
2. Modified Alyssa.txt (synthetic respiration from breath rates)

This shows how much accuracy we lose by not having real respiration hardware.

Usage:
    python3 test_synthetic_respiration.py
"""

import math
from pathlib import Path


def read_alyssa_file(filepath):
    """Read original Alyssa file."""
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Find data start (after "Sensor" line)
    data_start = 0
    header_lines = []
    for i, line in enumerate(lines):
        if line.strip().startswith('Sensor'):
            data_start = i + 2  # Skip sensor line and blank line
            header_lines = lines[:data_start]
            break

    # Parse data
    data = []
    for line in lines[data_start:]:
        parts = line.strip().split('\t')
        if len(parts) >= 2:
            try:
                ecg = float(parts[0])
                resp = float(parts[1])
                data.append((ecg, resp))
            except ValueError:
                continue

    return header_lines, data


def generate_synthetic_respiration(num_samples, sample_rate=256):
    """
    Generate synthetic respiration matching Alyssa session protocol.

    Alyssa session info from file:
    - Date: 01-07-2018
    - Duration: 985 seconds (16.4 minutes)
    - Session: SA95BP-6.75to4.25 (sliding 6.75 → 4.25 bpm)
    """

    # Session parameters
    duration = num_samples / sample_rate  # seconds (actual file duration)
    protocol_duration = 15 * 60  # 900 seconds (15-minute protocol)
    start_rate = 6.75  # bpm
    end_rate = 4.25    # bpm

    # Calculate rate change per second BASED ON 15-MINUTE PROTOCOL
    # (not compressed into the actual file duration!)
    rate_change_per_sec = (end_rate - start_rate) / protocol_duration

    # Respiration parameters (matching real data scale)
    baseline = 664.0
    amplitude = 15.0  # Small amplitude like real data

    respiration = []

    for i in range(num_samples):
        t = i / sample_rate  # Time in seconds

        # Current breathing rate (linear interpolation at 15-min protocol rate)
        # For 3.26 min file: starts at 6.75 bpm, ends at ~6.21 bpm
        # (NOT the full 4.25 bpm - that would take 15 minutes!)
        current_rate = start_rate + (rate_change_per_sec * t)

        # Convert to Hz
        freq_hz = current_rate / 60.0

        # Generate sine wave
        # Add small natural variation
        amp_variation = 1.0 + 0.1 * math.sin(t * 0.3)
        value = baseline + (amplitude * amp_variation * math.sin(2 * math.pi * freq_hz * t))

        respiration.append(value)

    return respiration


def write_modified_file(header_lines, ecg_data, resp_data, output_file):
    """Write modified file with synthetic respiration."""
    with open(output_file, 'w') as f:
        # Write header
        for line in header_lines:
            f.write(line)

        # Write data
        for ecg, resp in zip(ecg_data, resp_data):
            f.write(f"{ecg:.3f}\t{resp:.3f}\n")


def analyze_respiration_comparison(original_resp, synthetic_resp, sample_rate=256):
    """Compare original vs synthetic respiration characteristics."""

    print("\n" + "=" * 70)
    print("RESPIRATION COMPARISON ANALYSIS")
    print("=" * 70)

    # Basic statistics
    orig_mean = sum(original_resp) / len(original_resp)
    orig_min = min(original_resp)
    orig_max = max(original_resp)
    orig_range = orig_max - orig_min

    synth_mean = sum(synthetic_resp) / len(synthetic_resp)
    synth_min = min(synthetic_resp)
    synth_max = max(synthetic_resp)
    synth_range = synth_max - synth_min

    print(f"\nOriginal Respiration (Real Hardware):")
    print(f"  Mean: {orig_mean:.2f}")
    print(f"  Range: {orig_min:.2f} - {orig_max:.2f} (span: {orig_range:.2f})")

    print(f"\nSynthetic Respiration (breath.cafe simulation):")
    print(f"  Mean: {synth_mean:.2f}")
    print(f"  Range: {synth_min:.2f} - {synth_max:.2f} (span: {synth_range:.2f})")

    # Calculate amplitude match
    amplitude_match = (synth_range / orig_range) * 100
    print(f"\nAmplitude Match: {amplitude_match:.1f}%")

    if amplitude_match < 80 or amplitude_match > 120:
        print(f"  ⚠️  Warning: Amplitude mismatch > 20%")
    else:
        print(f"  ✅ Good amplitude match")

    # Sample data at regular intervals
    print(f"\nSample Comparison (every 60 seconds):")
    print(f"  Time  | Original | Synthetic | Difference")
    print(f"  ------|----------|-----------|------------")

    for i in range(0, len(original_resp), sample_rate * 60):
        if i < len(original_resp):
            time_min = i / sample_rate / 60
            orig_val = original_resp[i]
            synth_val = synthetic_resp[i]
            diff = abs(orig_val - synth_val)
            print(f"  {time_min:5.1f}m | {orig_val:8.2f} | {synth_val:9.2f} | {diff:10.2f}")


def main():
    """Run the test."""

    print("=" * 70)
    print("SYNTHETIC RESPIRATION IMPACT TEST")
    print("=" * 70)
    print("\nThis test compares:")
    print("1. Original Alyssa.txt (real NeXus-32 respiration data)")
    print("2. Modified version (synthetic breath.cafe respiration)")
    print("\nGoal: Quantify accuracy loss from using synthetic data")
    print("=" * 70)

    # Paths
    alyssa_file = Path("/Users/oli/Downloads/HRVISUALIZER_WITH_SOURCE_CODE/Nexus/Nexus/Alyssa-Short.txt")
    output_file = Path("/Users/oli/Downloads/HRVISUALIZER_WITH_SOURCE_CODE/test_data/Alyssa_Synthetic_Respiration.txt")

    if not alyssa_file.exists():
        print(f"\n❌ Error: Alyssa-Short.txt not found at {alyssa_file}")
        return

    # Read original file
    print(f"\n📖 Reading original file...")
    header_lines, data = read_alyssa_file(alyssa_file)

    ecg_data = [ecg for ecg, _ in data]
    original_resp = [resp for _, resp in data]

    print(f"✅ Loaded {len(data)} samples")
    print(f"   Duration: {len(data) / 256 / 60:.1f} minutes")

    # Generate synthetic respiration
    print(f"\n🫁 Generating synthetic respiration...")
    synthetic_resp = generate_synthetic_respiration(len(data))
    print(f"✅ Generated {len(synthetic_resp)} samples")

    # Analyze comparison
    analyze_respiration_comparison(original_resp, synthetic_resp)

    # Write modified file
    print(f"\n💾 Writing modified file...")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    write_modified_file(header_lines, ecg_data, synthetic_resp, output_file)
    print(f"✅ Written to: {output_file}")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("\n1. Import BOTH files into HRVisualizer on Windows:")
    print(f"   - Original: {alyssa_file.name}")
    print(f"   - Modified: {output_file.name}")
    print("\n2. Compare RF detection results:")
    print("   - Note the detected RF for each file")
    print("   - Calculate difference in bpm")
    print("\n3. This shows the accuracy impact of synthetic respiration!")
    print("\n" + "=" * 70)

    # Create comparison summary
    summary_file = output_file.parent / "RESPIRATION_TEST_SUMMARY.md"
    with open(summary_file, 'w') as f:
        f.write("# Synthetic Respiration Impact Test\n\n")
        f.write("## Test Files\n\n")
        f.write(f"1. **Original:** `Nexus/Nexus/Alyssa-Short.txt`\n")
        f.write(f"   - Real NeXus-32 respiration hardware data\n")
        f.write(f"   - Piezo-electric strain belt\n\n")
        f.write(f"2. **Modified:** `{output_file.name}`\n")
        f.write(f"   - Same ECG data (unchanged)\n")
        f.write(f"   - Synthetic respiration (simulated from breath.cafe rates)\n\n")
        f.write("## Purpose\n\n")
        f.write("Determine how much RF detection accuracy we lose by using:\n")
        f.write("- Polar H10 (no respiration hardware)\n")
        f.write("- breath.cafe visual pacer (no amplitude measurement)\n")
        f.write("- Synthetic respiration waveform (generated from breathing rates)\n\n")
        f.write("## Hypothesis\n\n")
        f.write("Synthetic respiration may cause RF detection errors because:\n")
        f.write("1. **No real amplitude data**: We don't know how DEEP the person breathed\n")
        f.write("2. **Perfect sine wave**: Real breathing has irregularities\n")
        f.write("3. **Estimated amplitude**: We guessed ±15 units based on Alyssa's data\n\n")
        f.write("## How to Test\n\n")
        f.write("### On Windows PC:\n\n")
        f.write("1. Open HRVisualizer (Nexus.exe)\n\n")
        f.write("2. Import original file:\n")
        f.write(f"   - File → Open → Alyssa-Short.txt\n")
        f.write(f"   - Note detected RF: ________ bpm\n\n")
        f.write("3. Import modified file:\n")
        f.write(f"   - File → Open → {output_file.name}\n")
        f.write(f"   - Note detected RF: ________ bpm\n\n")
        f.write("4. Calculate difference:\n")
        f.write(f"   - Difference: |Original RF - Modified RF| = ________ bpm\n\n")
        f.write("## Expected Results\n\n")
        f.write("**If difference < 0.3 bpm:**\n")
        f.write("- ✅ Synthetic respiration is GOOD ENOUGH\n")
        f.write("- Polar H10 + breath.cafe approach will work\n")
        f.write("- No need for respiration hardware\n\n")
        f.write("**If difference 0.3-0.5 bpm:**\n")
        f.write("- ⚠️ Synthetic respiration has moderate impact\n")
        f.write("- Results still usable for personal RF assessment\n")
        f.write("- Consider respiration hardware for research-grade accuracy\n\n")
        f.write("**If difference > 0.5 bpm:**\n")
        f.write("- ❌ Synthetic respiration significantly affects accuracy\n")
        f.write("- Need real respiration hardware (piezo belt)\n")
        f.write("- Current approach not suitable for precise RF detection\n\n")
        f.write("## Results\n\n")
        f.write("*Fill this in after testing on Windows:*\n\n")
        f.write("- **Original RF:** ________ bpm\n")
        f.write("- **Modified RF:** ________ bpm\n")
        f.write("- **Difference:** ________ bpm\n")
        f.write("- **Conclusion:** _______________________\n")

    print(f"\n📄 Created test summary: {summary_file}")


if __name__ == '__main__':
    main()
