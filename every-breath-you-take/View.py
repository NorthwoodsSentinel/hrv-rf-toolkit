import sys
import wave
import struct
import math
import os
import tempfile
from PySide6.QtCore import QTimer, Qt, QPointF, Slot, QUrl
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QSlider, QLabel, QWidget, QComboBox, QPushButton, QGraphicsDropShadowEffect, QLineEdit, QSpinBox
from PySide6.QtCharts import QChartView, QLineSeries, QScatterSeries, QAreaSeries
from PySide6.QtGui import QPen, QPainter, QColor, QDoubleValidator
from PySide6.QtMultimedia import QSoundEffect
import time
import numpy as np
import logging
import asyncio
from Model import Model
from sensor import SensorHandler
from views.widgets import CirclesWidget, SquareWidget
from views.charts import create_chart, create_scatter_series, create_line_series, create_spline_series, create_axis
from styles.colours import RED, YELLOW, ORANGE, GREEN, BLUE, GRAY, GOLD, LINEWIDTH, DOTSIZE_SMALL
from styles.utils import get_stylesheet


def _generate_click_wav(freq=900, duration=0.035, decay=80.0, volume=0.65):
    """Generate a short percussive click as a WAV file. Returns the file path."""
    sample_rate = 44100
    n = int(sample_rate * duration)
    path = os.path.join(tempfile.gettempdir(), f'ebyt_click_{freq}.wav')
    with wave.open(path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        samples = [
            int(math.sin(2 * math.pi * freq * i / sample_rate)
                * math.exp(-decay * i / sample_rate)
                * volume * 32767)
            for i in range(n)
        ]
        f.writeframes(struct.pack(f'{n}h', *samples))
    return path


class View(QChartView):
    

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.model = Model()
        self.model.sensor_connected.connect(self._on_sensor_connected)
        self.model.protocol_manager.adaptive_converged.connect(self._on_adaptive_converged)
        self.model.protocol_manager.adaptive_status_changed.connect(self._on_adaptive_status)
        self.model.protocol_manager.adaptive_queue_changed.connect(self._on_adaptive_queue_changed)

        self.adaptive_export_done = False  # Track whether we've already exported

        # Pacer sound cues
        self.sound_enabled = False
        try:
            click_path = _generate_click_wav(freq=900)
            url = QUrl.fromLocalFile(click_path)
            self._click_a = QSoundEffect()
            self._click_a.setSource(url)
            self._click_a.setVolume(0.6)
            self._click_b = QSoundEffect()   # second click for inhale
            self._click_b.setSource(url)
            self._click_b.setVolume(0.6)
            self._click_exhale = QSoundEffect()
            self._click_exhale.setSource(url)
            self._click_exhale.setVolume(0.4)  # slightly softer for exhale
            self._sounds_available = True
        except Exception as e:
            self._sounds_available = False
            logging.getLogger(__name__).warning(f"Sound unavailable: {e}")

        self.sensor_handler = SensorHandler()
        self.sensor_handler.scan_complete.connect(self._on_scan_complete)

        self.setStyleSheet(get_stylesheet("styles/style.qss"))

        # Series parameters
        self.UPDATE_SERIES_PERIOD = 100 # ms
        self.UPDATE_BREATHING_SERIES_PERIOD = 50 # ms
        self.UPDATE_PACER_PERIOD = 10 # 20 # ms
        self.PACER_HIST_SIZE = 6000
        self.BREATH_ACC_TIME_RANGE = 60 # s
        self.HR_SERIES_TIME_RANGE = 300 # s
        self.HRV_SERIES_TIME_RANGE = 300 # s

        # Initialisation
        self.pacer_rate = 6
        self.active_pacer_rate = 6  # Rate currently driving the pacer
        self.last_phase = "Exhale"  # Track phase for end-of-breath rate switching

        self.create_breath_chart()
        self.create_hrv_chart()
        self.create_circles_layout()
        self.set_view_layout()
        self.start_view_update()

        self.pacer_values_hist = np.full((self.PACER_HIST_SIZE, 1), np.nan)
        self.pacer_times_hist = np.full((self.PACER_HIST_SIZE, 1), np.nan)
        self.pacer_times_hist_rel_s = np.full(self.PACER_HIST_SIZE, np.nan) # relative seconds

    def create_breath_chart(self):
        '''
        Creates the breath chart which shows pacer, heart rate, and chest acceleration
        '''
        # Breathing acceleration
        self.chart_breath = create_chart(title='Breathing Acceleration', showTitle=False, showLegend=False)
        self.series_pacer = create_line_series(GOLD, LINEWIDTH)
        self.series_breath_acc = create_line_series(BLUE, LINEWIDTH)
        self.series_breath_cycle_marker = create_scatter_series(GRAY, DOTSIZE_SMALL)
        self.axis_acc_x = create_axis(title=None, tickCount=10, rangeMin=-self.BREATH_ACC_TIME_RANGE, rangeMax=0, labelSize=10, flip=False)
        # self.axis_y_pacer = create_axis(title="Pacer", color=GOLD, rangeMin=-1, rangeMax=1)
        self.axis_y_breath_acc = create_axis("Chest expansion (m/s2)", BLUE, rangeMin=-1, rangeMax=1, labelSize=10)

        self.series_hr = create_scatter_series(RED, DOTSIZE_SMALL)
        self.axis_hr_y = create_axis(title="HR (bpm)", color=RED, rangeMin=50, rangeMax=80, labelSize=10)

        # Configure
        self.chart_breath.addSeries(self.series_pacer)
        self.chart_breath.addSeries(self.series_breath_acc)
        self.chart_breath.addSeries(self.series_breath_cycle_marker)
        self.chart_breath.addSeries(self.series_hr)
        self.chart_breath.addAxis(self.axis_acc_x, Qt.AlignBottom)
        self.chart_breath.addAxis(self.axis_y_breath_acc, Qt.AlignRight)
        self.chart_breath.addAxis(self.axis_hr_y, Qt.AlignLeft)
        self.series_pacer.attachAxis(self.axis_acc_x)
        self.series_pacer.attachAxis(self.axis_y_breath_acc)
        self.series_breath_acc.attachAxis(self.axis_acc_x)
        self.series_breath_acc.attachAxis(self.axis_y_breath_acc)
        self.series_breath_cycle_marker.attachAxis(self.axis_acc_x)
        self.series_breath_cycle_marker.attachAxis(self.axis_y_breath_acc)
        self.series_hr.attachAxis(self.axis_acc_x)
        self.series_hr.attachAxis(self.axis_hr_y)

    def create_hrv_chart(self):
        '''
        Chart showing breathing rate and heart rate variability
        '''
        # Heart rate variability chart
        self.chart_hrv = create_chart(title='Heart rate variability', showTitle=False, showLegend=False)

        # Breathing rate
        self.series_br = create_spline_series(BLUE, LINEWIDTH)
        self.series_br_marker = create_scatter_series(BLUE, DOTSIZE_SMALL)
        self.series_br_marker.setMarkerShape(QScatterSeries.MarkerShapeTriangle)
        self.axis_br_y = create_axis(title="BR (bpm)", color=BLUE, rangeMin=0, rangeMax=20, labelSize=10)\
        
        # self.series_hrv = create_spline_series(RED, LINEWIDTH)
        self.series_maxmin = create_spline_series(RED, LINEWIDTH)
        self.series_maxmin_marker = create_scatter_series(RED, DOTSIZE_SMALL)
        self.series_rmssd60 = create_spline_series(ORANGE, LINEWIDTH)
        self.series_rmssd60_marker = create_scatter_series(ORANGE, DOTSIZE_SMALL)
        self.axis_hrv_x = create_axis(title=None, tickCount=10, rangeMin=-self.HRV_SERIES_TIME_RANGE, rangeMax=0, labelSize=10)
        self.axis_hrv_y = create_axis(title="maxmin / RMSSD-60s (ms)", color=RED, rangeMin=0, rangeMax=300, labelSize=10)

        self.hrv_band_line_0 = QLineSeries()
        self.hrv_band_line_0.append(-self.HRV_SERIES_TIME_RANGE, 0)
        self.hrv_band_line_0.append(0, 0)
        self.hrv_band_line_1 = QLineSeries()
        self.hrv_band_line_1.append(-self.HRV_SERIES_TIME_RANGE, 50)
        self.hrv_band_line_1.append(0, 50)
        self.hrv_band_line_2 = QLineSeries()
        self.hrv_band_line_2.append(-self.HRV_SERIES_TIME_RANGE, 150)
        self.hrv_band_line_2.append(0, 150)
        self.hrv_band_line_3 = QLineSeries()
        self.hrv_band_line_3.append(-self.HRV_SERIES_TIME_RANGE, 2000)
        self.hrv_band_line_3.append(0, 2000)
        self.hrv_band_0 = QAreaSeries(self.hrv_band_line_0, self.hrv_band_line_1)
        self.hrv_band_0.setColor(RED)
        self.hrv_band_0.setOpacity(0.2)
        self.hrv_band_0.setPen(QPen(Qt.NoPen))
        self.hrv_band_1 = QAreaSeries(self.hrv_band_line_1, self.hrv_band_line_2)
        self.hrv_band_1.setColor(YELLOW)
        self.hrv_band_1.setOpacity(0.2)
        self.hrv_band_1.setPen(QPen(Qt.NoPen))
        self.hrv_band_2 = QAreaSeries(self.hrv_band_line_2, self.hrv_band_line_3)
        self.hrv_band_2.setColor(GREEN)
        self.hrv_band_2.setOpacity(0.2)
        self.hrv_band_2.setPen(QPen(Qt.NoPen))

        # Heart rate variability chart
        # self.chart_hrv.addSeries(self.series_hrv)
        self.chart_hrv.addSeries(self.hrv_band_0)
        self.chart_hrv.addSeries(self.hrv_band_1)
        self.chart_hrv.addSeries(self.hrv_band_2)
        self.chart_hrv.addSeries(self.series_maxmin)
        self.chart_hrv.addSeries(self.series_maxmin_marker)
        self.chart_hrv.addSeries(self.series_rmssd60)
        self.chart_hrv.addSeries(self.series_rmssd60_marker)
        self.chart_hrv.addAxis(self.axis_hrv_x, Qt.AlignBottom)
        self.chart_hrv.addAxis(self.axis_hrv_y, Qt.AlignLeft)
        self.series_maxmin.attachAxis(self.axis_hrv_x)
        self.series_maxmin.attachAxis(self.axis_hrv_y)
        self.series_maxmin_marker.attachAxis(self.axis_hrv_x)
        self.series_maxmin_marker.attachAxis(self.axis_hrv_y)
        self.series_rmssd60.attachAxis(self.axis_hrv_x)
        self.series_rmssd60.attachAxis(self.axis_hrv_y)
        self.series_rmssd60_marker.attachAxis(self.axis_hrv_x)
        self.series_rmssd60_marker.attachAxis(self.axis_hrv_y)
        self.hrv_band_0.attachAxis(self.axis_hrv_x)
        self.hrv_band_0.attachAxis(self.axis_hrv_y)
        self.hrv_band_1.attachAxis(self.axis_hrv_x)
        self.hrv_band_1.attachAxis(self.axis_hrv_y)
        self.hrv_band_2.attachAxis(self.axis_hrv_x)
        self.hrv_band_2.attachAxis(self.axis_hrv_y)

        # Breathing rate on HRV chart
        # self.chart_hrv.addSeries(self.series_br)
        self.chart_hrv.addSeries(self.series_br_marker)
        self.chart_hrv.addAxis(self.axis_br_y, Qt.AlignRight)
        # self.series_br.attachAxis(self.axis_hrv_x)
        # self.series_br.attachAxis(self.axis_br_y)
        self.series_br_marker.attachAxis(self.axis_hrv_x)
        self.series_br_marker.attachAxis(self.axis_br_y)

    def create_circles_layout(self):

        self.circles_widget = CirclesWidget(*self.model.pacer.update(self.pacer_rate), GOLD, BLUE, RED)
        self.circles_widget.setRenderHint(QPainter.Antialiasing)

        # BPM editable text input (allows decimals, e.g. 4.5)
        self.bpm_input = QLineEdit()
        self.bpm_input.setFixedWidth(60)
        self.bpm_input.setAlignment(Qt.AlignHCenter)
        _bpm_validator = QDoubleValidator(1.5, 30.0, 2)
        _bpm_validator.setNotation(QDoubleValidator.StandardNotation)
        self.bpm_input.setValidator(_bpm_validator)
        self.bpm_input.setText(f"{self.pacer_rate:.1f}")
        self.bpm_input.editingFinished.connect(self._on_bpm_input_changed)

        self.pacer_slider = QSlider(Qt.Horizontal)
        self.pacer_slider.setRange(3*2, 10*2)
        self.pacer_slider.setValue(int(self.pacer_rate * 2))
        self.pacer_slider.valueChanged.connect(self.update_pacer_rate)

        # Protocol controls
        self.protocol_label = QLabel("Protocol:")
        self.protocol_label.setStyleSheet("QLabel {color: black}")
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(self.model.protocol_manager.get_protocol_names())
        self.protocol_combo.currentTextChanged.connect(self._on_protocol_changed)

        self.session_button = QPushButton("Start Session")
        self.session_button.clicked.connect(self._on_session_button_press)

        self.timer_label = QLabel("00:00")
        self.timer_label.setStyleSheet("QLabel {color: black; font-size: 14px; font-weight: bold}")
        self.timer_label.setAlignment(Qt.AlignHCenter)
        self.timer_label.setFixedWidth(60)

        # Bracket width control for Adaptive Refine
        self.bracket_label = QLabel("\u00b1")
        self.bracket_label.setStyleSheet("QLabel {color: black}")
        self.bracket_slider = QSlider(Qt.Horizontal)
        self.bracket_slider.setRange(1, 10)  # 0.25 to 2.5 in steps of 0.25
        self.bracket_slider.setValue(4)  # default ±1.0
        self.bracket_slider.setFixedWidth(80)
        self.bracket_slider.valueChanged.connect(self._on_bracket_changed)
        self.bracket_value_label = QLabel("\u00b11.0")
        self.bracket_value_label.setStyleSheet("QLabel {color: black}")
        self.bracket_value_label.setFixedWidth(35)
        # Hidden by default, shown when Adaptive_Refine selected
        self.bracket_label.setVisible(False)
        self.bracket_slider.setVisible(False)
        self.bracket_value_label.setVisible(False)

        # Duration control for Timed_Manual
        self.duration_label = QLabel("Duration:")
        self.duration_label.setStyleSheet("QLabel {color: black}")
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(1, 120)
        self.duration_spinbox.setValue(10)
        self.duration_spinbox.setSuffix(" min")
        self.duration_spinbox.setFixedWidth(80)
        self.duration_spinbox.valueChanged.connect(self._on_duration_changed)
        self.duration_label.setVisible(False)
        self.duration_spinbox.setVisible(False)

        # Sound cue toggle
        self.sound_button = QPushButton("Sound: Off")
        self.sound_button.setCheckable(True)
        self.sound_button.setChecked(False)
        self.sound_button.setFixedWidth(90)
        self.sound_button.clicked.connect(self._on_sound_toggle)
        if not self._sounds_available:
            self.sound_button.setEnabled(False)
            self.sound_button.setToolTip("Sound unavailable")

        # circles_layout: just the circle widget (slider/protocol moved to main layout)
        circlesVBox = QVBoxLayout()
        circlesVBox.addWidget(self.circles_widget, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        self.circles_layout = SquareWidget()
        self.circles_layout.setLayout(circlesVBox)

    def _create_scale_controls(self):
        '''Create scale adjustment controls for HR and HRV charts'''
        # HR Y-axis scale
        hr_scale_layout = QHBoxLayout()
        hr_scale_label = QLabel("HR:")
        hr_scale_label.setStyleSheet("QLabel {color: black; font-size: 11px}")
        hr_scale_label.setFixedWidth(30)
        self.hr_scale_slider = QSlider(Qt.Horizontal)
        self.hr_scale_slider.setRange(0, 4)  # index into preset ranges
        self.hr_scale_slider.setValue(1)  # default: 50-80
        self.hr_scale_slider.setFixedWidth(80)
        self.hr_scale_slider.valueChanged.connect(self._on_hr_scale_changed)
        self.hr_scale_value_label = QLabel("50-80")
        self.hr_scale_value_label.setStyleSheet("QLabel {color: black; font-size: 11px}")
        self.hr_scale_value_label.setFixedWidth(50)
        hr_scale_layout.addWidget(hr_scale_label)
        hr_scale_layout.addWidget(self.hr_scale_slider)
        hr_scale_layout.addWidget(self.hr_scale_value_label)

        # HRV Y-axis scale
        hrv_scale_layout = QHBoxLayout()
        hrv_scale_label = QLabel("HRV:")
        hrv_scale_label.setStyleSheet("QLabel {color: black; font-size: 11px}")
        hrv_scale_label.setFixedWidth(30)
        self.hrv_scale_slider = QSlider(Qt.Horizontal)
        self.hrv_scale_slider.setRange(0, 4)  # index into preset ranges
        self.hrv_scale_slider.setValue(2)  # default: 0-250
        self.hrv_scale_slider.setFixedWidth(80)
        self.hrv_scale_slider.valueChanged.connect(self._on_hrv_scale_changed)
        self.hrv_scale_value_label = QLabel("0-250")
        self.hrv_scale_value_label.setStyleSheet("QLabel {color: black; font-size: 11px}")
        self.hrv_scale_value_label.setFixedWidth(50)
        hrv_scale_layout.addWidget(hrv_scale_label)
        hrv_scale_layout.addWidget(self.hrv_scale_slider)
        hrv_scale_layout.addWidget(self.hrv_scale_value_label)

        scale_layout = QVBoxLayout()
        scale_label = QLabel("Scale")
        scale_label.setStyleSheet("QLabel {color: black; font-size: 11px; font-weight: bold}")
        scale_label.setAlignment(Qt.AlignHCenter)
        scale_layout.addStretch()
        scale_layout.addWidget(scale_label)
        scale_layout.addLayout(hr_scale_layout)
        scale_layout.addLayout(hrv_scale_layout)
        scale_layout.addStretch()

        scale_widget = QWidget()
        scale_widget.setLayout(scale_layout)
        scale_widget.setFixedWidth(180)
        return scale_widget

    def _on_hr_scale_changed(self, index):
        '''Adjust HR chart Y-axis range'''
        hr_ranges = [
            (50, 70, "50-70"),
            (50, 80, "50-80"),
            (40, 100, "40-100"),
            (40, 120, "40-120"),
            (30, 150, "30-150"),
        ]
        lo, hi, label = hr_ranges[index]
        self.axis_hr_y.setRange(lo, hi)
        self.hr_scale_value_label.setText(label)

    def _on_hrv_scale_changed(self, index):
        '''Adjust HRV chart Y-axis range'''
        hrv_ranges = [
            (0, 50, "0-50"),
            (0, 100, "0-100"),
            (0, 250, "0-250"),
            (0, 500, "0-500"),
            (0, 1000, "0-1000"),
        ]
        lo, hi, label = hrv_ranges[index]
        self.axis_hrv_y.setRange(lo, hi)
        self.hrv_scale_value_label.setText(label)

    def set_view_layout(self):

        layout = QVBoxLayout()
        graphLayout = QVBoxLayout()

        acc_widget = QChartView(self.chart_breath)
        acc_widget.setStyleSheet("background-color: transparent;")
        hrv_widget = QChartView(self.chart_hrv)
        hrv_widget.setStyleSheet("background-color: transparent;")
        acc_widget.setRenderHint(QPainter.Antialiasing)
        hrv_widget.setRenderHint(QPainter.Antialiasing)

        scale_widget = self._create_scale_controls()

        topRowLayout = QHBoxLayout()
        topRowLayout.addWidget(self.circles_layout, stretch=1)
        topRowLayout.addWidget(acc_widget, stretch=3)

        # BPM slider row (full width, no longer cramped in SquareWidget)
        bpm_row_label = QLabel("BPM:")
        bpm_row_label.setStyleSheet("QLabel {color: black}")
        sliderRow = QHBoxLayout()
        sliderRow.addWidget(bpm_row_label)
        sliderRow.addWidget(self.bpm_input)
        sliderRow.addWidget(self.pacer_slider, stretch=1)

        # Protocol controls row (full width)
        protocolRow = QHBoxLayout()
        protocolRow.addWidget(self.protocol_label)
        protocolRow.addWidget(self.protocol_combo)
        protocolRow.addSpacing(8)
        protocolRow.addWidget(self.bracket_label)
        protocolRow.addWidget(self.bracket_slider)
        protocolRow.addWidget(self.bracket_value_label)
        protocolRow.addWidget(self.duration_label)
        protocolRow.addWidget(self.duration_spinbox)
        protocolRow.addSpacing(8)
        protocolRow.addWidget(self.session_button)
        protocolRow.addSpacing(8)
        protocolRow.addWidget(self.timer_label)
        protocolRow.addSpacing(8)
        protocolRow.addWidget(self.sound_button)
        protocolRow.addStretch()

        self.message_box = QLabel("Scanning...")
        self.message_box.setFixedWidth(350)
        self.message_box.setFixedHeight(15)
        self.message_box.setAlignment(Qt.AlignLeft)

        self.queue_label = QLabel("")
        self.queue_label.setFixedHeight(15)
        self.queue_label.setAlignment(Qt.AlignLeft)
        self.queue_label.setStyleSheet("QLabel {color: #888; font-size: 11px}")
        self.queue_label.setVisible(False)

        self.scan_button = QPushButton("Scan")
        self.scan_button.clicked.connect(self._on_scan_button_press)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(20, 20)
        shadow.setColor(QColor(255, 255, 255, 255))  # Semi-transparent black shadow
        self.scan_button.setGraphicsEffect(shadow)

        self.device_menu = QComboBox()
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self._on_connect_button_press)

        # Export button for HRVisualizer
        self.export_button = QPushButton("Export to HRVisualizer")
        self.export_button.clicked.connect(self._on_export_button_press)
        self.export_button.setEnabled(False)  # Enable after sensor connects

        controlLayout = QHBoxLayout()
        controlLayout.addStretch(1)
        controlLayout.addWidget(self.message_box)
        controlLayout.addWidget(self.queue_label)
        # controlLayout.addStretch(1)
        controlLayout.addWidget(self.scan_button)
        controlLayout.addWidget(self.device_menu)
        controlLayout.addWidget(self.connect_button)
        controlLayout.addWidget(self.export_button)
        controlLayout.addStretch(2)
        
        controlWidget = QWidget()
        controlWidget.setObjectName("controlWidget")
        controlWidget.setLayout(controlLayout)

        hrvRowLayout = QHBoxLayout()
        hrvRowLayout.addWidget(hrv_widget, stretch=3)
        hrvRowLayout.addWidget(scale_widget, stretch=0)

        graphLayout.addLayout(topRowLayout, stretch=1)
        graphLayout.addLayout(sliderRow, stretch=0)
        graphLayout.addLayout(protocolRow, stretch=0)
        graphLayout.addLayout(hrvRowLayout, stretch=1)
        graphLayout.setContentsMargins(0, 0, 0, 0)

        layout.addLayout(graphLayout, stretch=10)
        layout.addWidget(controlWidget, stretch=1)

        self.setLayout(layout)

    def start_view_update(self):

        self.update_series_timer = QTimer()
        self.update_series_timer.timeout.connect(self.update_series)
        self.update_series_timer.setInterval(self.UPDATE_SERIES_PERIOD)

        self.update_acc_series_timer = QTimer()
        self.update_acc_series_timer.timeout.connect(self.update_acc_series)
        self.update_acc_series_timer.setInterval(self.UPDATE_BREATHING_SERIES_PERIOD)
        
        self.pacer_timer = QTimer()
        self.pacer_timer.setInterval(self.UPDATE_PACER_PERIOD)  # ms (20 Hz)
        self.pacer_timer.timeout.connect(self.plot_circles)

        self.update_acc_series_timer.start()
        self.update_series_timer.start()
        self.pacer_timer.start()

    def update_pacer_rate(self):
        self.pacer_rate = self.pacer_slider.value() / 2
        if not self.bpm_input.hasFocus():
            self.bpm_input.setText(f"{self.pacer_rate:.1f}")

    def plot_circles(self):
        # Get target breathing rate from protocol manager
        target_rate = self.model.protocol_manager.get_current_breathing_rate(self.pacer_rate)

        # Only apply rate changes at end of exhale (exhale→inhale transition)
        # This prevents jarring mid-breath rate jumps and ensures the algorithm
        # only counts HRV from breaths actually taken at the new rate
        phase_text = self.model.pacer.get_phase_label(self.active_pacer_rate)
        if self.last_phase == "Exhale" and phase_text == "Inhale":
            # Transition point - apply any pending rate change
            if target_rate != self.active_pacer_rate:
                self.active_pacer_rate = target_rate
                self.model.protocol_manager.confirm_rate_applied()
            self._play_phase_sound("Inhale")
        elif self.last_phase == "Inhale" and phase_text == "Exhale":
            self._play_phase_sound("Exhale")
        if self.model.protocol_manager.current_protocol in ("Manual", "Timed_Manual"):
            # Manual/Timed modes: apply rate changes immediately (user is dragging slider)
            self.active_pacer_rate = target_rate
        self.last_phase = phase_text

        current_pacer_rate = self.active_pacer_rate

        # Update slider and input to reflect protocol rate
        if self.model.protocol_manager.is_running and self.model.protocol_manager.current_protocol not in ("Manual", "Timed_Manual"):
            self.pacer_slider.setValue(int(current_pacer_rate * 2))
            if not self.bpm_input.hasFocus():
                self.bpm_input.setText(f"{current_pacer_rate:.2f}")

        # Update timer if session is running
        if self.model.protocol_manager.is_running:
            session_info = self.model.protocol_manager.get_session_info()
            mins = int(session_info["elapsed"] // 60)
            secs = int(session_info["elapsed"] % 60)
            self.timer_label.setText(f"{mins:02d}:{secs:02d}")

            # Auto-export and stop when Fisher & Lehrer completes
            if session_info["is_complete"] and self.model.protocol_manager.is_fisher_lehrer_protocol():
                self.model.stop_recording_session()
                self.session_button.setText("Start Session")
                self.message_box.setText("Session complete - exporting...")
                # Auto-export
                output_path = self.model.export_to_hrvisualizer()
                if output_path:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self,
                        "Fisher & Lehrer Complete!",
                        f"15-minute protocol complete!\n\nExported to:\n{output_path}\n\nTransfer to Windows and import to HRVisualizer to see your RF!"
                    )

            # Timed Manual: stop sounds and session when duration expires
            if session_info["is_complete"] and self.model.protocol_manager.is_timed_manual_protocol():
                self.model.stop_recording_session()
                self.session_button.setText("Start Session")
                if self.sound_enabled:
                    self.sound_enabled = False
                    self.sound_button.setChecked(False)
                    self.sound_button.setText("Sound: Off")
                elapsed = session_info["elapsed"]
                self.message_box.setText(
                    f"Timed session complete ({int(elapsed // 60)}:{int(elapsed % 60):02d})"
                )

            # Adaptive protocols: stop if 15 min timeout without convergence
            if session_info["is_complete"] and self.model.protocol_manager.is_adaptive_protocol():
                if not self.model.protocol_manager.adaptive_converged_flag:
                    pm = self.model.protocol_manager
                    best = pm.adaptive_best_rate
                    self.model.stop_recording_session()
                    self.session_button.setText("Start Session")
                    output_path = self.model.export_to_hrvisualizer()
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self,
                        "Adaptive Timeout",
                        f"15-minute limit reached without full convergence.\n\n"
                        f"Best rate found: {best:.2f} bpm\n\n"
                        f"Exported to:\n{output_path}" if output_path else
                        f"15-minute limit reached. Best rate: {best:.2f} bpm"
                    )

        # Pacer
        coordinates = self.model.pacer.update(current_pacer_rate)
        self.circles_widget.update_pacer_series(*coordinates)
        self.circles_widget.update_phase_label(phase_text)

        self.pacer_values_hist = np.roll(self.pacer_values_hist, -1)
        self.pacer_values_hist[-1] = np.linalg.norm([coordinates[0][0],coordinates[1][0]]) - 0.5
        self.pacer_times_hist = np.roll(self.pacer_times_hist, -1)
        self.pacer_times_hist[-1] = time.time_ns()/1.0e9

        # Breathing
        breath_coordinates = self.model.breath_analyser.get_breath_circle_coords()
        self.circles_widget.update_breath_series(*breath_coordinates)

    def update_acc_series(self):
        
        self.pacer_times_hist_rel_s = self.pacer_times_hist - time.time_ns()/1.0e9
            
        series_breath_acc_new = self.model.breath_analyser.chest_acc_history.get_qpoint_list()
        self.series_breath_acc.replace(series_breath_acc_new)
        
        series_breath_cycle_marker_new = self.model.breath_analyser.chest_acc_history.get_qpoint_marker_list()
        self.series_breath_cycle_marker.replace(series_breath_cycle_marker_new)

        series_pacer_new = []
        for i, value in enumerate(self.pacer_times_hist_rel_s):
            if not np.isnan(value):
                series_pacer_new.append(QPointF(value, self.pacer_values_hist[i]))
                
        if series_pacer_new:
            self.series_pacer.replace(series_pacer_new)

    def update_series(self):

        series_hr_new = self.model.hrv_analyser.hr_history.get_qpoint_list()
        self.series_hr.replace(series_hr_new)

        # Breathing rate plot
        series_br_new = self.model.breath_analyser.br_history.get_qpoint_list()
        self.series_br.replace(series_br_new)
        self.series_br_marker.replace(series_br_new)

        # maxmin (RSA amplitude, red) and RMSSD-60s (EliteHRV-comparable, orange)
        series_maxmin_new = self.model.hrv_analyser.maxmin_history.get_qpoint_list()
        self.series_maxmin.replace(series_maxmin_new)
        self.series_maxmin_marker.replace(series_maxmin_new)

        series_rmssd60_new = self.model.hrv_analyser.rmssd_60s_history.get_qpoint_list()
        self.series_rmssd60.replace(series_rmssd60_new)
        self.series_rmssd60_marker.replace(series_rmssd60_new)

    async def set_first_sensor_found(self):
        ''' List valid devices and connect to first one'''
        
        valid_devices = self.sensor_handler.get_valid_device_names()
        
        selected_device_name = str(valid_devices[0]) # Select first device
        self.logger.info(f"Connecting to {selected_device_name}")
        sensor = self.sensor_handler.create_sensor_client(selected_device_name)
        await self.set_sensor(sensor)

    async def set_sensor(self, sensor):
        try:
            await self.model.set_and_connect_sensor(sensor)
        except Exception as e:
            self.logger.error(f"Error: Failed to connect – {e}")
            sys.exit(1)

    async def main(self):
        await self.sensor_handler.scan()

    @Slot()
    def _on_scan_button_press(self):
        self.message_box.setText("Scanning...")
        asyncio.create_task(self.sensor_handler.scan())

    @Slot()
    def _on_scan_complete(self):
        self.message_box.setText("Select a sensor")
        self.device_menu.clear()
        self.device_menu.addItems(self.sensor_handler.get_valid_device_names())

    @Slot()
    def _on_connect_button_press(self):
        ''' Connect to the sensor selected in the device menu
        '''
        self.message_box.setText("Connecting...")
        selected_device_name = self.device_menu.currentText()
        self.logger.info(f"Conencting to sensor: {selected_device_name}")
        if not selected_device_name:
            return
        sensor = self.sensor_handler.create_sensor_client(selected_device_name)
        asyncio.create_task(self.set_sensor(sensor))
    
    @Slot()
    def _on_sensor_connected(self):
        self.message_box.setText("Connected")
        self.export_button.setEnabled(True)  # Enable export after connection

    @Slot()
    def _on_export_button_press(self):
        '''Export collected data to HRVisualizer format'''
        from PySide6.QtWidgets import QMessageBox

        self.message_box.setText("Exporting...")
        output_path = self.model.export_to_hrvisualizer()

        if output_path:
            self.message_box.setText("Export complete!")
            QMessageBox.information(
                self,
                "Export Complete",
                f"Data exported successfully!\n\n{output_path}\n\nTransfer to Windows and import to HRVisualizer."
            )
        else:
            self.message_box.setText("Export failed")
            QMessageBox.warning(
                self,
                "Export Failed",
                "Not enough data to export. Record for at least 1 minute."
            )

    @Slot()
    def _on_protocol_changed(self, protocol_name):
        '''Handle protocol selection change'''
        self.model.protocol_manager.set_protocol(protocol_name)
        desc = self.model.protocol_manager.get_protocol_description(protocol_name)
        self.protocol_combo.setToolTip(desc)
        # Show/hide bracket width control
        show_bracket = (protocol_name == "Adaptive_Refine")
        self.bracket_label.setVisible(show_bracket)
        self.bracket_slider.setVisible(show_bracket)
        self.bracket_value_label.setVisible(show_bracket)
        # Show/hide duration control
        show_duration = (protocol_name == "Timed_Manual")
        self.duration_label.setVisible(show_duration)
        self.duration_spinbox.setVisible(show_duration)
        # Clear queue label when switching protocols
        self.queue_label.setText("")
        self.queue_label.setVisible(False)

    @Slot()
    def _on_bracket_changed(self):
        '''Update bracket half-width for Adaptive Refine'''
        half_width = self.bracket_slider.value() * 0.25  # 0.25 to 2.5
        self.bracket_value_label.setText(f"\u00b1{half_width:.2g}")
        self.model.protocol_manager.refine_bracket_half = half_width

    @Slot()
    def _on_session_button_press(self):
        '''Start/Stop protocol session'''
        if not self.model.protocol_manager.is_running:
            # Start session (also sets recording timestamp)
            self.adaptive_export_done = False
            self.active_pacer_rate = self.pacer_rate  # Sync active rate with slider
            self.last_phase = "Exhale"
            self.model.start_recording_session()
            self.session_button.setText("Stop Session")
            self.message_box.setText("Session running...")
        else:
            # Stop session
            self.model.stop_recording_session()
            self.session_button.setText("Start Session")
            self.message_box.setText("Session stopped")
            self.queue_label.setText("")
            self.queue_label.setVisible(False)

    @Slot(float)
    def _on_adaptive_converged(self, rf_rate):
        '''Handle adaptive protocol convergence - auto-export then hold'''
        if self.adaptive_export_done:
            return
        self.adaptive_export_done = True

        self.message_box.setText(f"RF = {rf_rate:.2f} bpm - exporting...")
        output_path = self.model.export_to_hrvisualizer()

        from PySide6.QtWidgets import QMessageBox
        if output_path:
            QMessageBox.information(
                self,
                "Adaptive RF Found!",
                f"Resonance frequency found: {rf_rate:.2f} bpm\n\n"
                f"Exported to:\n{output_path}\n\n"
                f"Pacer will continue at this rate."
            )
        self.message_box.setText(f"Holding at RF = {rf_rate:.2f} bpm")

    @Slot(str)
    def _on_adaptive_status(self, status_text):
        '''Update message box with adaptive protocol status'''
        self.message_box.setText(status_text)

    @Slot(object)
    def _on_adaptive_queue_changed(self, upcoming_rates):
        '''Show/update upcoming test rates queue label'''
        if upcoming_rates and len(upcoming_rates) > 1:
            rates_str = " \u2192 ".join(f"{r:.2f}" for r in upcoming_rates)
            self.queue_label.setText(f"Next: {rates_str} bpm")
            self.queue_label.setVisible(True)
        else:
            self.queue_label.setText("")
            self.queue_label.setVisible(False)

    @Slot()
    def _on_sound_toggle(self):
        '''Toggle pacer sound cues on/off'''
        self.sound_enabled = self.sound_button.isChecked()
        self.sound_button.setText("Sound: On" if self.sound_enabled else "Sound: Off")

    @Slot()
    def _on_bpm_input_changed(self):
        '''Handle direct BPM text entry (accepts decimals like 4.5)'''
        try:
            rate = float(self.bpm_input.text().replace(',', '.'))
            rate = max(1.5, min(30.0, rate))
            self.pacer_rate = rate
            # Sync slider to nearest 0.5 step within its range (block to avoid feedback loop)
            slider_val = max(self.pacer_slider.minimum(),
                             min(self.pacer_slider.maximum(), int(round(rate * 2))))
            self.pacer_slider.blockSignals(True)
            self.pacer_slider.setValue(slider_val)
            self.pacer_slider.blockSignals(False)
            self.bpm_input.setText(f"{rate:.2f}")
        except ValueError:
            self.bpm_input.setText(f"{self.pacer_rate:.1f}")

    @Slot(int)
    def _on_duration_changed(self, minutes):
        '''Update Timed_Manual session duration'''
        self.model.protocol_manager.set_timed_duration(minutes * 60)

    def _play_phase_sound(self, phase):
        '''Play click sound(s) on pacer phase transition.
        Inhale = 2 clicks (120ms apart), Exhale = 1 softer click.'''
        if not self.sound_enabled or not self._sounds_available:
            return
        if phase == "Inhale":
            self._click_a.play()
            QTimer.singleShot(120, self._click_b.play)
        else:
            self._click_exhale.play()