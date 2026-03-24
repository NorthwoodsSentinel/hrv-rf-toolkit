"""
DataExporter - Export Polar H10 data to HRVisualizer format

Converts real-time collected data to HRVisualizer-compatible NeXus format:
- RR intervals from Polar H10 → ECG waveform reconstruction
- Accelerometer breathing → Real respiration waveform
- Perfect synchronization (same device!)
"""

import numpy as np
import math
from datetime import datetime
from pathlib import Path


class DataExporter:
    """Exports Polar H10 data to HRVisualizer-compatible format"""

    def __init__(self):
        self.sample_rate = 256  # HRVisualizer expects 256 Hz

    def export_to_hrvisualizer(self, ibi_history, breath_acc_history, output_path, session_name="Polar H10 RF Test", export_raw=True, session_start_time=None):
        """
        Export collected data to HRVisualizer format.

        Args:
            ibi_history: HistoryBuffer with RR intervals (times, values in ms)
            breath_acc_history: HistoryBuffer with chest acceleration
            output_path: Where to save the .txt file
            session_name: Session name for header
            export_raw: If True, also export raw data for debugging
            session_start_time: Only export data from this timestamp onward (epoch seconds)
        """
        print("=" * 70)
        print("EXPORTING TO HRVISUALIZER FORMAT")
        print("=" * 70)

        # Get data from history buffers
        ibi_times = ibi_history.times[~np.isnan(ibi_history.times)]
        ibi_values = ibi_history.values[~np.isnan(ibi_history.values)][:len(ibi_times)]

        breath_times = breath_acc_history.times[~np.isnan(breath_acc_history.times)]
        breath_values = breath_acc_history.values[~np.isnan(breath_acc_history.values)][:len(breath_times)]

        # Filter data to only include data from session start onward
        if session_start_time is not None:
            print(f"\n📍 Session start time: {session_start_time:.1f}s")

            # Filter RR data
            ibi_mask = ibi_times >= session_start_time
            ibi_times_before = len(ibi_times)
            ibi_times = ibi_times[ibi_mask]
            ibi_values = ibi_values[ibi_mask]
            print(f"   RR intervals: {ibi_times_before} → {len(ibi_times)} (removed {ibi_times_before - len(ibi_times)} preroll samples)")

            # Filter breathing data
            breath_mask = breath_times >= session_start_time
            breath_times_before = len(breath_times)
            breath_times = breath_times[breath_mask]
            breath_values = breath_values[breath_mask]
            print(f"   Breathing samples: {breath_times_before} → {len(breath_times)} (removed {breath_times_before - len(breath_times)} preroll samples)")

        if len(ibi_times) == 0 or len(breath_times) == 0:
            print("❌ No data to export!")
            return False

        print(f"\n📊 Data Summary:")
        print(f"   RR intervals: {len(ibi_values)}")
        print(f"   RR time range: {ibi_times[0]:.1f} → {ibi_times[-1]:.1f} ({ibi_times[-1] - ibi_times[0]:.1f}s)")
        print(f"   Breath samples: {len(breath_values)}")
        print(f"   Breath time range: {breath_times[0]:.1f} → {breath_times[-1]:.1f} ({breath_times[-1] - breath_times[0]:.1f}s)")

        # Determine time range - use OVERLAPPING period only
        start_time = max(ibi_times[0], breath_times[0])  # Start when BOTH are available
        end_time = min(ibi_times[-1], breath_times[-1])  # End when either stops
        duration = end_time - start_time

        if duration <= 0:
            print("❌ No overlapping data between RR and breathing!")
            return False

        print(f"\n⚠️  Time alignment:")
        print(f"   RR starts: {ibi_times[0]:.1f}s")
        print(f"   Breathing starts: {breath_times[0]:.1f}s")
        print(f"   Gap: {abs(ibi_times[0] - breath_times[0]):.1f}s")
        print(f"   Using overlapping range: {start_time:.1f} → {end_time:.1f}")
        print(f"   Export duration: {duration:.1f} seconds ({duration/60:.2f} minutes)")

        # Calculate number of samples at 256 Hz
        num_samples = int(duration * self.sample_rate)

        print(f"\n🫀 Reconstructing ECG from {len(ibi_values)} RR intervals...")
        ecg_data = self._reconstruct_ecg_from_ibi(ibi_times, ibi_values, start_time, num_samples)

        print(f"🫁 Converting chest acceleration to respiration waveform...")
        resp_data = self._convert_breathing_to_respiration(breath_times, breath_values, start_time, num_samples)

        print(f"\n💾 Writing HRVisualizer file: {output_path}")
        self._write_hrvisualizer_file(output_path, ecg_data, resp_data, session_name)

        # Export raw data for debugging
        if export_raw:
            raw_path = str(output_path).replace('.txt', '_raw.txt')
            print(f"📝 Writing raw data debug file: {raw_path}")
            self._write_raw_debug_file(raw_path, ibi_times, ibi_values, breath_times, breath_values)

        print("\n" + "=" * 70)
        print("✅ EXPORT COMPLETE!")
        print("=" * 70)
        print(f"\n📁 HRVisualizer file: {output_path}")
        print(f"📊 Samples: {len(ecg_data):,} ({len(ecg_data)/self.sample_rate/60:.2f} minutes)")
        if export_raw:
            print(f"📝 Raw debug file: {raw_path}")
        print(f"\n🎯 Next steps:")
        print(f"   1. Transfer {Path(output_path).name} to Windows PC")
        print(f"   2. Open HRVisualizer")
        print(f"   3. Import the file")
        print(f"   4. Your RF will be displayed!")
        print("=" * 70)

        return True

    def _reconstruct_ecg_from_ibi(self, ibi_times, ibi_values, start_time, num_samples):
        """
        Reconstruct ECG waveform from inter-beat intervals.

        Creates simplified PQRST complexes at each heartbeat location.
        """
        # Initialize ECG array with baseline
        ecg = np.full(num_samples, 16700.0)

        # Convert IBI times to sample indices
        current_time = start_time
        current_sample = 0

        for ibi_ms in ibi_values:
            # Calculate samples until next R-wave
            samples_to_next = int((ibi_ms / 1000.0) * self.sample_rate)
            current_sample += samples_to_next

            # Place R-wave at current position
            if current_sample < num_samples:
                # Generate simplified R-wave (large negative spike)
                for j in range(-3, 4):
                    sample_idx = current_sample + j
                    if 0 <= sample_idx < num_samples:
                        dist = abs(j)
                        if dist == 0:
                            ecg[sample_idx] = 16700.0 - 9000  # R-wave peak
                        else:
                            ecg[sample_idx] = 16700.0 - 9000 * (1.0 - dist / 3.0)

        return ecg

    def _convert_breathing_to_respiration(self, breath_times, breath_values, start_time, num_samples):
        """
        Convert chest acceleration to respiration waveform.

        Interpolates accelerometer readings to 256 Hz and scales to match
        NeXus respiration format (baseline ~664, amplitude ~30 units).
        """
        # Create time array for output samples
        end_time = start_time + (num_samples / self.sample_rate)
        sample_times = np.linspace(start_time, end_time, num_samples)

        # Filter breathing data to only the time range we need
        # This avoids interpolation issues at the boundaries
        valid_idx = (breath_times >= start_time) & (breath_times <= end_time)
        breath_times_filtered = breath_times[valid_idx]
        breath_values_filtered = breath_values[valid_idx]

        print(f"   Breathing samples in range: {len(breath_values_filtered)} / {len(breath_values)}")

        if len(breath_values_filtered) < 2:
            print("   ⚠️  WARNING: Very few breathing samples in time range!")
            print("   Using all available breathing data instead...")
            breath_times_filtered = breath_times
            breath_values_filtered = breath_values

        # Interpolate breath acceleration to 256 Hz
        # np.interp will extrapolate with edge values outside the data range
        breath_interp = np.interp(sample_times, breath_times_filtered, breath_values_filtered)

        # Scale to NeXus respiration range
        # Real NeXus: baseline ~664, range ±15-30 units
        breath_min = np.min(breath_values_filtered)  # Use filtered data for scaling
        breath_max = np.max(breath_values_filtered)
        breath_range = breath_max - breath_min

        print(f"   Breathing range: {breath_min:.3f} → {breath_max:.3f} (Δ{breath_range:.3f})")

        if breath_range > 0.001:  # Small threshold to avoid division by zero
            # Normalize to 0-1
            normalized = (breath_interp - breath_min) / breath_range
            # Scale to NeXus range (baseline 664, ±30 amplitude)
            baseline = 664.0
            amplitude = 30.0
            resp_data = baseline + (normalized - 0.5) * amplitude * 2
        else:
            # If no breathing detected, flat line
            print("   ⚠️  WARNING: No breathing variation detected!")
            resp_data = np.full(num_samples, 664.0)

        return resp_data

    def _write_hrvisualizer_file(self, output_path, ecg_data, resp_data, session_name):
        """Write HRVisualizer-compatible NeXus format file."""

        # Ensure equal lengths
        min_len = min(len(ecg_data), len(resp_data))
        ecg_data = ecg_data[:min_len]
        resp_data = resp_data[:min_len]

        now = datetime.now()
        duration_sec = len(ecg_data) / self.sample_rate

        with open(output_path, 'w') as f:
            # Write NeXus header
            f.write(f"Client:\t,{session_name}\n")
            f.write(f"Session:\tPolarH10-EBYT-Export\n")
            f.write(f"Date:\t{now.strftime('%m-%d-%Y')}\n")
            f.write(f"Time:\t{now.strftime('%H:%M:%S')}\n")
            f.write(f"Output rate:\t256\tSamples/sec.\n")
            f.write(f"\n")
            f.write(f"Sensor\n")
            f.write(f"\n")

            # Write data (ECG, Respiration)
            for ecg, resp in zip(ecg_data, resp_data):
                f.write(f"{ecg:.3f}\t{resp:.3f}\n")

    def _write_raw_debug_file(self, output_path, ibi_times, ibi_values, breath_times, breath_values):
        """Write raw data for debugging purposes."""
        with open(output_path, 'w') as f:
            f.write("# RAW DATA DEBUG FILE\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("#\n")
            f.write(f"# RR Intervals: {len(ibi_values)} samples\n")
            f.write(f"# RR Time Range: {ibi_times[0]:.3f} → {ibi_times[-1]:.3f} ({ibi_times[-1] - ibi_times[0]:.3f}s)\n")
            f.write(f"#\n")
            f.write(f"# Breathing: {len(breath_values)} samples\n")
            f.write(f"# Breath Time Range: {breath_times[0]:.3f} → {breath_times[-1]:.3f} ({breath_times[-1] - breath_times[0]:.3f}s)\n")
            f.write(f"#\n")
            f.write(f"# Time Gap: {abs(ibi_times[0] - breath_times[0]):.3f}s\n")
            f.write("#\n\n")

            # Write RR intervals
            f.write("=== RR INTERVALS (time, value_ms) ===\n")
            for t, v in zip(ibi_times, ibi_values):
                f.write(f"{t:.6f}\t{v:.3f}\n")

            f.write("\n=== BREATHING ACCELERATION (time, value) ===\n")
            for t, v in zip(breath_times, breath_values):
                f.write(f"{t:.6f}\t{v:.6f}\n")
