import numpy as np
from Pacer import Pacer
from blehrm.interface import BlehrmClientInterface
import logging
from PySide6.QtCore import QObject, Signal
from analysis.HrvAnalyser import HrvAnalyser
from analysis.BreathAnalyser import BreathAnalyser
from DataExporter import DataExporter
from ProtocolManager import ProtocolManager
from datetime import datetime

class Model(QObject):

    sensor_connected = Signal()
    protocol_changed = Signal(str)
    export_complete = Signal(str)  # Emits filepath when export completes

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.sensor_client = None
        self.pacer = Pacer()

        self.hrv_analyser = HrvAnalyser()
        self.breath_analyser = BreathAnalyser()
        self.data_exporter = DataExporter()
        self.protocol_manager = ProtocolManager()

        # Session tracking - only export data from when session starts
        self.session_start_timestamp = None

        # Give protocol manager access to HRV data for adaptive modes
        self.protocol_manager.set_hrv_analyser(self.hrv_analyser)

        # Connect protocol changes
        self.protocol_manager.protocol_changed.connect(self.protocol_changed.emit)
        
    async def set_and_connect_sensor(self, sensor: BlehrmClientInterface):
        self.sensor_client = sensor
        await self.sensor_client.connect()
        await self.sensor_client.get_device_info()
        await self.sensor_client.print_device_info()

        # Configure breath analyser for Polar H10
        # This enables proper subsampling (200 Hz → 10 Hz) and prevents buffer overflow
        sensor_class_name = sensor.__class__.__name__
        self.logger.info(f"Configuring BreathAnalyser for sensor: {sensor_class_name}")
        if "PolarH10" in sensor_class_name or "Polar" in str(sensor):
            self.breath_analyser.set_analysis_params_by_sensor_class("PolarH10Client")

        await self.sensor_client.start_ibi_stream(callback=self.handle_ibi_callback)
        await self.sensor_client.start_acc_stream(callback=self.handle_acc_callback)

        self.sensor_connected.emit()

    async def disconnect_sensor(self):
        await self.sensor_client.disconnect()

    def start_recording_session(self):
        """Start a recording session - marks the timestamp for data export"""
        import time
        self.session_start_timestamp = time.time()
        self.protocol_manager.start_session()
        self.logger.info(f"Recording session started at {self.session_start_timestamp}")

    def stop_recording_session(self):
        """Stop the recording session"""
        self.protocol_manager.stop_session()
        self.logger.info("Recording session stopped")

    def handle_ibi_callback(self, data):

        t, ibi = data
        self.hrv_analyser.update(t, ibi)

    def handle_acc_callback(self, data):
        '''
        Handles reading accelerometer for the sensor
        Updates the breath_analyser which calculates breathing rate
        One each breath, hrv_analyser calculates metrics
        '''
        t = data[0]
        acc = data[1:]
        self.breath_analyser.update_chest_acc(t, acc)

        # Breath-by-breath analysis
        if self.breath_analyser.is_end_of_breath and not self.breath_analyser.br_history.is_empty():

            t_range = self.breath_analyser.get_last_breath_t_range()
            self.hrv_analyser.update_breath_by_breath_metrics(t_range)

            # Update protocol manager for per-breath rate changes (Fisher & Lehrer)
            self.protocol_manager.on_breath_complete()

    def export_to_hrvisualizer(self, output_dir="exports"):
        """
        Export collected data to HRVisualizer format.

        Args:
            output_dir: Directory to save export files

        Returns:
            Path to exported file, or None if export failed
        """
        import os
        from pathlib import Path

        # Create exports directory if it doesn't exist
        Path(output_dir).mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        protocol_name = self.protocol_manager.current_protocol.replace('_', '-')
        filename = f"rf_test_{protocol_name}_{timestamp}.txt"
        output_path = os.path.join(output_dir, filename)

        # Export data (only from session start if timestamp is set)
        success = self.data_exporter.export_to_hrvisualizer(
            ibi_history=self.hrv_analyser.ibi_history,
            breath_acc_history=self.breath_analyser.chest_acc_history,
            output_path=output_path,
            session_name=f"Polar H10 {protocol_name} {timestamp}",
            session_start_time=self.session_start_timestamp
        )

        if success:
            self.export_complete.emit(output_path)
            self._append_rf_session_summary(output_dir, timestamp, protocol_name)
            return output_path
        else:
            return None

    def _append_rf_session_summary(self, output_dir, timestamp, protocol_name):
        """Append per-session HRV statistics to rf_history.json for multi-session RF tracking."""
        import json, os
        from pathlib import Path

        # Compute statistics from the session window (session_start_timestamp onwards)
        t_start = self.session_start_timestamp if self.session_start_timestamp else 0

        # maxmin samples during session
        maxmin_vals = self.hrv_analyser.maxmin_history
        ids = maxmin_vals.times >= t_start
        mm_data = maxmin_vals.values[ids]
        mm_data = mm_data[~np.isnan(mm_data)]

        # RMSSD-60s samples during session
        rmssd_vals = self.hrv_analyser.rmssd_60s_history
        ids_r = rmssd_vals.times >= t_start
        rmssd_data = rmssd_vals.values[ids_r]
        rmssd_data = rmssd_data[~np.isnan(rmssd_data)]

        if len(mm_data) < 2:
            self.logger.info("RF history: not enough data to save session summary")
            return

        # For adaptive refine, record what the best/converged rate was
        pm = self.protocol_manager
        if pm.adaptive_converged_flag and pm.adaptive_best_rate > 0:
            session_rate = round(pm.adaptive_best_rate, 3)
        elif pm.adaptive_current_rate > 0:
            session_rate = round(pm.adaptive_current_rate, 3)
        else:
            session_rate = None  # Fisher & Lehrer or manual - no single rate

        entry = {
            "timestamp": timestamp,
            "protocol": protocol_name,
            "session_rate_bpm": session_rate,
            "n_breaths": int(pm.breath_count),
            "maxmin_mean_ms": round(float(np.mean(mm_data)), 1),
            "maxmin_sd_ms": round(float(np.std(mm_data, ddof=1)), 1) if len(mm_data) > 1 else None,
            "rmssd60_mean_ms": round(float(np.mean(rmssd_data)), 1) if len(rmssd_data) > 0 else None,
            "rmssd60_sd_ms": round(float(np.std(rmssd_data, ddof=1)), 1) if len(rmssd_data) > 1 else None,
        }

        history_path = os.path.join(output_dir, "rf_history.json")
        history = []
        if Path(history_path).exists():
            try:
                with open(history_path, "r") as f:
                    history = json.load(f)
            except (json.JSONDecodeError, IOError):
                history = []

        history.append(entry)
        with open(history_path, "w") as f:
            json.dump(history, f, indent=2)

        self.logger.info(
            f"RF history: saved session summary to {history_path} — "
            f"rate={session_rate} bpm, maxmin={entry['maxmin_mean_ms']}±{entry['maxmin_sd_ms']}ms, "
            f"RMSSD-60s={entry['rmssd60_mean_ms']}ms"
        )
