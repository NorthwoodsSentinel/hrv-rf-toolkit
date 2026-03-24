"""
ProtocolManager - Breathing Protocol Management

Implements multiple breathing protocols:
- Fisher & Lehrer: Research-validated sliding RF determination
- Adaptive Explore: Hill-climbing search for unknown RF
- Adaptive Refine: Bracket-and-bisect fine-tuning around estimated RF

Fisher, L.R., Lehrer, P.M. (2022). A Method for More Accurate Determination
of Resonance Frequency of the Cardiovascular System.
Applied Psychophysiology and Biofeedback, 47, 17-26.
"""

import time
import logging
import numpy as np
from PySide6.QtCore import QObject, Signal


class ProtocolManager(QObject):
    """Manages breathing protocols including adaptive RF determination"""

    protocol_changed = Signal(str)  # Emits protocol name when changed
    adaptive_converged = Signal(float)  # Emits converged RF rate in bpm
    adaptive_status_changed = Signal(str)  # Emits status text for UI
    adaptive_queue_changed = Signal(object)  # Emits list of upcoming test rates

    # Adaptive algorithm constants
    ADAPTIVE_MIN_RATE = 3.5  # bpm
    ADAPTIVE_MAX_RATE = 7.0  # bpm
    ADAPTIVE_DWELL_BREATHS = 6  # breaths to dwell at each test rate (after entrainment)
    ADAPTIVE_ENTRAIN_GRACE_BREATHS = 2  # breaths to discard after each rate switch (entrainment lag)
    ADAPTIVE_CONVERGENCE_STEP = 0.1  # bpm - converged when step < this
    ADAPTIVE_EXPLORE_START_RATE = 5.5  # bpm
    ADAPTIVE_EXPLORE_INITIAL_STEP = 0.5  # bpm
    ADAPTIVE_REFINE_BRACKET_HALF_DEFAULT = 1.0  # bpm each side of start (UI-adjustable)
    ADAPTIVE_REFINE_CONVERGE_WIDTH = 0.2  # bpm - bracket width to stop

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.protocols = {
            "Manual": {
                "name": "Manual Control",
                "description": "Set your own breathing rate with slider",
                "start_rate": 6.0,
                "end_rate": 6.0,
                "duration": None,
                "mode": "manual"
            },
            "Fisher_Lehrer": {
                "name": "Fisher & Lehrer RF Test",
                "description": "15-min research protocol (6.75\u21924.25 bpm)",
                "start_rate": 6.75,
                "end_rate": 4.25,
                "duration": 900,  # 15 minutes in seconds
                "mode": "automatic"
            },
            "Adaptive_Explore": {
                "name": "Adaptive RF Explorer",
                "description": "Auto-finds RF via hill climbing (start 5.5 bpm, range 3.5-7.0)",
                "start_rate": 5.5,
                "end_rate": None,
                "duration": 900,  # 15 min max
                "mode": "adaptive_explore"
            },
            "Adaptive_Refine": {
                "name": "Adaptive RF Refine",
                "description": "Fine-tunes RF around slider rate (\u00b11.0 bpm bracket)",
                "start_rate": None,  # uses slider value
                "end_rate": None,
                "duration": 900,  # 15 min max
                "mode": "adaptive_refine"
            },
            "HeartMath": {
                "name": "HeartMath Coherence",
                "description": "Fixed 6 bpm (~0.1 Hz resonance)",
                "start_rate": 6.0,
                "end_rate": 6.0,
                "duration": None,
                "mode": "fixed"
            },
            "Custom_5bpm": {
                "name": "Custom 5 bpm",
                "description": "Fixed 5 bpm breathing",
                "start_rate": 5.0,
                "end_rate": 5.0,
                "duration": None,
                "mode": "fixed"
            },
            "Timed_Manual": {
                "name": "Timed Manual",
                "description": "Manual rate control — sounds stop automatically after set duration",
                "start_rate": 6.0,
                "end_rate": 6.0,
                "duration": 600,  # 10 minutes default, UI-adjustable
                "mode": "timed_manual"
            }
        }

        self.current_protocol = "Manual"
        self.session_start_time = None
        self.is_running = False

        # Per-breath discrete rate tracking for Fisher & Lehrer
        self.breath_count = 0
        self.current_breath_period_ms = 0  # Current period in milliseconds
        self.period_change_per_breath_ms = 0  # Period increment per breath

        # HRV analyser reference (set by Model)
        self.hrv_analyser = None

        # Configurable refine bracket (UI can change this)
        self.refine_bracket_half = self.ADAPTIVE_REFINE_BRACKET_HALF_DEFAULT

        # Adaptive protocol state
        self._reset_adaptive_state()

    def _reset_adaptive_state(self):
        """Reset all adaptive algorithm state"""
        self.adaptive_current_rate = 0.0  # Current test rate in bpm
        self.adaptive_dwell_count = 0  # Breaths at current test rate (after entrainment)
        self.adaptive_entrain_count = 0  # Breaths discarded for entrainment after rate switch
        self.adaptive_hrv_samples = []  # maxmin samples at current rate
        self.adaptive_best_rate = 0.0  # Best rate found so far
        self.adaptive_best_hrv = 0.0  # HRV at best rate
        self.adaptive_converged_flag = False
        self.adaptive_initial_rate_set = False  # For Refine: has slider rate been captured
        self.adaptive_rate_pending = False  # True while waiting for View to apply rate

        # Explore-specific (hill climbing)
        self.adaptive_step_size = self.ADAPTIVE_EXPLORE_INITIAL_STEP
        self.adaptive_direction = -1  # Start by going slower (down in bpm)
        self.adaptive_prev_hrv = 0.0  # HRV at previous test rate
        self.adaptive_reversals = 0  # Number of direction reversals

        # Refine-specific (bracket and bisect)
        self.adaptive_phase = "coarse"
        self.adaptive_bracket = [self.ADAPTIVE_MIN_RATE, self.ADAPTIVE_MAX_RATE]
        self.adaptive_all_results = []  # persistent (rate, hrv) across all rounds
        self.adaptive_coarse_index = 0  # which coarse point we're testing
        self.adaptive_coarse_points = []  # current round's test points

    def set_hrv_analyser(self, hrv_analyser):
        """Set reference to HRV analyser for reading per-breath metrics"""
        self.hrv_analyser = hrv_analyser

    def get_protocol_names(self):
        """Return list of protocol names for UI dropdown"""
        return list(self.protocols.keys())

    def get_protocol_description(self, protocol_name):
        """Get description of a protocol"""
        if protocol_name in self.protocols:
            return self.protocols[protocol_name]["description"]
        return ""

    def set_protocol(self, protocol_name):
        """Set the current protocol"""
        if protocol_name in self.protocols:
            self.current_protocol = protocol_name
            self.protocol_changed.emit(protocol_name)
            return True
        return False

    def start_session(self):
        """Start a new session"""
        self.session_start_time = time.time()
        self.is_running = True

        protocol = self.protocols[self.current_protocol]

        # Initialize per-breath tracking for Fisher & Lehrer
        if protocol["mode"] == "automatic":
            start_rate = protocol["start_rate"]
            end_rate = protocol["end_rate"]
            duration = protocol["duration"]

            start_period_ms = (60.0 / start_rate) * 1000.0
            end_period_ms = (60.0 / end_rate) * 1000.0

            avg_rate = (start_rate + end_rate) / 2.0
            expected_total_breaths = (duration / 60.0) * avg_rate

            total_period_change_ms = end_period_ms - start_period_ms
            self.period_change_per_breath_ms = total_period_change_ms / expected_total_breaths

            self.breath_count = 0
            self.current_breath_period_ms = start_period_ms

        # Initialize adaptive protocols
        elif protocol["mode"] == "adaptive_explore":
            self._reset_adaptive_state()
            self.adaptive_current_rate = self.ADAPTIVE_EXPLORE_START_RATE
            self.adaptive_initial_rate_set = True
            self.current_breath_period_ms = (60.0 / self.adaptive_current_rate) * 1000.0
            self.breath_count = 0
            self.logger.info(f"Adaptive Explore started at {self.adaptive_current_rate:.2f} bpm")
            self.adaptive_status_changed.emit(
                f"Exploring: {self.adaptive_current_rate:.1f} bpm | Dwelling..."
            )

        elif protocol["mode"] == "adaptive_refine":
            self._reset_adaptive_state()
            # Rate will be captured from slider on first get_current_breathing_rate() call
            self.adaptive_initial_rate_set = False
            self.breath_count = 0
            self.logger.info("Adaptive Refine waiting for slider rate")

    def stop_session(self):
        """Stop the current session"""
        self.is_running = False

    def reset_session(self):
        """Reset session timer"""
        self.session_start_time = None
        self.is_running = False
        self.breath_count = 0
        self.current_breath_period_ms = 0
        self.period_change_per_breath_ms = 0
        self._reset_adaptive_state()

    def _get_latest_maxmin(self):
        """Get the latest maxmin value from HRV analyser"""
        if self.hrv_analyser is None:
            return None
        values = self.hrv_analyser.maxmin_history.values
        # Get last non-NaN value
        valid = values[~np.isnan(values)]
        if len(valid) == 0:
            return None
        return float(valid[-1])

    def _clamp_rate(self, rate):
        """Clamp rate to valid range"""
        return max(self.ADAPTIVE_MIN_RATE, min(self.ADAPTIVE_MAX_RATE, rate))

    # ── Adaptive Explore: Hill Climbing ──────────────────────────────

    def _adaptive_explore_step(self):
        """
        Hill climbing algorithm for finding RF.
        Called after dwelling at a rate for ADAPTIVE_DWELL_BREATHS.
        """
        current_hrv = np.mean(self.adaptive_hrv_samples)
        self.logger.info(
            f"Explore: rate={self.adaptive_current_rate:.2f} bpm, "
            f"HRV maxmin={current_hrv:.1f}ms, step={self.adaptive_step_size:.2f}, "
            f"dir={self.adaptive_direction:+d}"
        )

        # Track best
        if current_hrv > self.adaptive_best_hrv:
            self.adaptive_best_hrv = current_hrv
            self.adaptive_best_rate = self.adaptive_current_rate

        # First evaluation - just record baseline and take first step
        if self.adaptive_prev_hrv == 0.0:
            self.adaptive_prev_hrv = current_hrv
            new_rate = self._clamp_rate(
                self.adaptive_current_rate + self.adaptive_direction * self.adaptive_step_size
            )
            self._set_adaptive_rate(new_rate)
            return

        # Compare with previous rate's HRV
        if current_hrv >= self.adaptive_prev_hrv:
            # Improving - keep going same direction
            self.adaptive_prev_hrv = current_hrv
            new_rate = self._clamp_rate(
                self.adaptive_current_rate + self.adaptive_direction * self.adaptive_step_size
            )
            # If we hit a boundary, reverse
            if new_rate == self.adaptive_current_rate:
                self.adaptive_direction *= -1
                self.adaptive_reversals += 1
                new_rate = self._clamp_rate(
                    self.adaptive_current_rate + self.adaptive_direction * self.adaptive_step_size
                )
            self._set_adaptive_rate(new_rate)
        else:
            # Worsening - reverse direction, halve step size
            self.adaptive_direction *= -1
            self.adaptive_step_size /= 2.0
            self.adaptive_reversals += 1
            self.adaptive_prev_hrv = current_hrv

            # Check convergence
            if self.adaptive_step_size < self.ADAPTIVE_CONVERGENCE_STEP:
                self._on_adaptive_converged()
                return

            new_rate = self._clamp_rate(
                self.adaptive_current_rate + self.adaptive_direction * self.adaptive_step_size
            )
            self._set_adaptive_rate(new_rate)

        self.adaptive_status_changed.emit(
            f"Exploring: {self.adaptive_current_rate:.2f} bpm | "
            f"HRV: {current_hrv:.0f}ms | Step: {self.adaptive_step_size:.2f}"
        )

    # ── Adaptive Refine: Bracket and Bisect ──────────────────────────

    def _init_refine_coarse_points(self, center_rate):
        """Set up the 3 coarse test points for bracket-and-bisect"""
        low = self._clamp_rate(center_rate - self.refine_bracket_half)
        high = self._clamp_rate(center_rate + self.refine_bracket_half)
        mid = (low + high) / 2.0

        self.adaptive_bracket = [low, high]
        self.adaptive_coarse_points = [low, mid, high]
        self.adaptive_coarse_index = 0
        self.adaptive_all_results = []
        self.adaptive_phase = "coarse"

        # Start at first coarse point
        self._set_adaptive_rate(self.adaptive_coarse_points[0])
        self.logger.info(
            f"Refine: coarse sweep [{low:.2f}, {mid:.2f}, {high:.2f}] bpm "
            f"(bracket \u00b1{self.refine_bracket_half:.1f})"
        )
        self.adaptive_status_changed.emit(
            f"Refine: testing {low:.2f} bpm (1/3) | Bracket \u00b1{self.refine_bracket_half:.1f}"
        )
        self.adaptive_queue_changed.emit(list(self.adaptive_coarse_points))

    def _adaptive_refine_step(self):
        """
        Bracket-and-bisect algorithm for fine-tuning RF.
        Called after dwelling at a rate for ADAPTIVE_DWELL_BREATHS.
        """
        current_hrv = np.mean(self.adaptive_hrv_samples)
        self.logger.info(
            f"Refine ({self.adaptive_phase}): rate={self.adaptive_current_rate:.2f} bpm, "
            f"HRV maxmin={current_hrv:.1f}ms"
        )

        # Track best overall
        if current_hrv > self.adaptive_best_hrv:
            self.adaptive_best_hrv = current_hrv
            self.adaptive_best_rate = self.adaptive_current_rate

        # Store result persistently
        self.adaptive_all_results.append((self.adaptive_current_rate, current_hrv))

        if self.adaptive_phase == "coarse":
            self.adaptive_coarse_index += 1
            if self.adaptive_coarse_index < len(self.adaptive_coarse_points):
                # Move to next coarse point
                self._set_adaptive_rate(self.adaptive_coarse_points[self.adaptive_coarse_index])
                self.adaptive_status_changed.emit(
                    f"Refine: testing {self.adaptive_current_rate:.2f} bpm "
                    f"({self.adaptive_coarse_index + 1}/{len(self.adaptive_coarse_points)}) | "
                    f"HRV: {current_hrv:.0f}ms"
                )
                self.adaptive_queue_changed.emit(
                    list(self.adaptive_coarse_points[self.adaptive_coarse_index:])
                )
            else:
                # Coarse sweep done - narrow bracket and schedule next tests
                self._start_bisect_phase()

    def _start_bisect_phase(self):
        """After coarse sweep, narrow or shift bracket and schedule next tests.

        Interior best → narrow bracket to [left_neighbour, right_neighbour] and
        test the midpoint of each sub-bracket (not the known best again).

        Edge best → shift bracket outward so best becomes the new centre and
        test the new unexplored boundary points.

        Always stays in "coarse" phase - no separate bisect phase needed.
        """
        sorted_points = sorted(self.adaptive_all_results, key=lambda p: p[0])
        best_idx = max(range(len(sorted_points)), key=lambda i: sorted_points[i][1])
        best_rate = sorted_points[best_idx][0]

        at_low_edge = (best_idx == 0)
        at_high_edge = (best_idx == len(sorted_points) - 1)

        if at_low_edge or at_high_edge:
            # Best at edge: shift bracket outward to explore beyond current range
            old_bracket = self.adaptive_bracket[:]
            new_low = self._clamp_rate(best_rate - self.refine_bracket_half)
            new_high = self._clamp_rate(best_rate + self.refine_bracket_half)

            if new_low == old_bracket[0] and new_high == old_bracket[1]:
                # Already at rate limits, can't expand - converge on best
                self.logger.info(
                    f"Refine: best at edge ({best_rate:.2f}) but at rate limits, converging"
                )
                self._on_adaptive_converged()
                return

            self.adaptive_bracket = [new_low, new_high]
            mid = (new_low + new_high) / 2.0
            candidate_points = [new_low, mid, new_high]
            self.logger.info(
                f"Refine: edge best ({best_rate:.2f}), shifting to [{new_low:.2f}, {new_high:.2f}]"
            )
        else:
            # Best in interior: narrow bracket to neighbours
            new_low = sorted_points[best_idx - 1][0]
            new_high = sorted_points[best_idx + 1][0]

            bracket_width = new_high - new_low
            if bracket_width < self.ADAPTIVE_REFINE_CONVERGE_WIDTH:
                self.logger.info(
                    f"Refine: bracket [{new_low:.2f}, {new_high:.2f}] < "
                    f"{self.ADAPTIVE_REFINE_CONVERGE_WIDTH} bpm, converging at {best_rate:.2f}"
                )
                self._on_adaptive_converged()
                return

            # Test midpoints of each sub-bracket (not the known best itself)
            lower_mid = (new_low + best_rate) / 2.0
            upper_mid = (best_rate + new_high) / 2.0
            candidate_points = [lower_mid, upper_mid]
            self.adaptive_bracket = [new_low, new_high]
            self.logger.info(
                f"Refine: interior best ({best_rate:.2f}), bracket [{new_low:.2f}, {new_high:.2f}], "
                f"testing sub-midpoints [{lower_mid:.2f}, {upper_mid:.2f}]"
            )

        # Filter to only untested points (within 0.02 bpm tolerance)
        new_coarse = [p for p in candidate_points
                      if not any(abs(r - p) < 0.02 for r, _ in self.adaptive_all_results)]

        if not new_coarse:
            self.logger.info("Refine: all candidate points already tested, converging")
            self._on_adaptive_converged()
            return

        self.adaptive_coarse_points = new_coarse
        self.adaptive_coarse_index = 0
        self.adaptive_phase = "coarse"
        self._set_adaptive_rate(self.adaptive_coarse_points[0])

        self.adaptive_status_changed.emit(
            f"Refine: testing {self.adaptive_current_rate:.2f} bpm | "
            f"Bracket: [{self.adaptive_bracket[0]:.2f}\u2013{self.adaptive_bracket[1]:.2f}] | "
            f"Best: {best_rate:.2f}"
        )
        self.adaptive_queue_changed.emit(list(self.adaptive_coarse_points))

    # ── Shared Adaptive Helpers ──────────────────────────────────────

    def _set_adaptive_rate(self, rate):
        """Set a new adaptive test rate (pending until View confirms it's applied)"""
        self.adaptive_current_rate = self._clamp_rate(rate)
        self.current_breath_period_ms = (60.0 / self.adaptive_current_rate) * 1000.0
        self.adaptive_dwell_count = 0
        self.adaptive_entrain_count = 0
        self.adaptive_hrv_samples = []
        self.adaptive_rate_pending = True  # Don't count breaths until View applies this

    def confirm_rate_applied(self):
        """Called by View when the pacer actually switches to the pending rate.

        This ensures HRV samples are only collected once the user is actually
        breathing at the new rate, not during the transition from the old rate.
        The entrainment grace period (ADAPTIVE_ENTRAIN_GRACE_BREATHS) then
        discards the first few breaths while RSA re-entrains to the new frequency.
        """
        if self.adaptive_rate_pending:
            self.adaptive_rate_pending = False
            self.adaptive_dwell_count = 0
            self.adaptive_entrain_count = 0
            self.adaptive_hrv_samples = []
            self.logger.info(
                f"Rate confirmed applied: {self.adaptive_current_rate:.2f} bpm, "
                f"discarding {self.ADAPTIVE_ENTRAIN_GRACE_BREATHS} entrainment breaths "
                f"then collecting {self.ADAPTIVE_DWELL_BREATHS} samples"
            )

    def _on_adaptive_converged(self):
        """Called when adaptive algorithm has converged"""
        self.adaptive_converged_flag = True
        self.adaptive_current_rate = self.adaptive_best_rate
        self.current_breath_period_ms = (60.0 / self.adaptive_best_rate) * 1000.0

        self.logger.info(
            f"Adaptive CONVERGED: RF = {self.adaptive_best_rate:.2f} bpm "
            f"(HRV maxmin = {self.adaptive_best_hrv:.1f}ms)"
        )
        self.adaptive_status_changed.emit(
            f"Converged! RF = {self.adaptive_best_rate:.2f} bpm "
            f"(HRV: {self.adaptive_best_hrv:.0f}ms)"
        )
        self.adaptive_queue_changed.emit([])
        self.adaptive_converged.emit(self.adaptive_best_rate)

    # ── Core Protocol Interface ──────────────────────────────────────

    def on_breath_complete(self):
        """
        Called when a complete breath cycle is detected.
        Routes to the appropriate protocol handler.
        """
        protocol = self.protocols[self.current_protocol]
        if not self.is_running:
            return

        self.breath_count += 1

        if protocol["mode"] == "automatic":
            # Fisher & Lehrer: increase period per breath
            self.current_breath_period_ms += self.period_change_per_breath_ms
            end_rate = protocol["end_rate"]
            end_period_ms = (60.0 / end_rate) * 1000.0
            if self.current_breath_period_ms > end_period_ms:
                self.current_breath_period_ms = end_period_ms

        elif protocol["mode"] in ("adaptive_explore", "adaptive_refine"):
            if self.adaptive_converged_flag:
                return  # Already converged, just hold

            # Don't count breaths while waiting for View to apply the new rate
            if self.adaptive_rate_pending:
                return

            # Discard first N breaths after rate switch for RSA re-entrainment
            if self.adaptive_entrain_count < self.ADAPTIVE_ENTRAIN_GRACE_BREATHS:
                self.adaptive_entrain_count += 1
                self.logger.debug(
                    f"Entraining: {self.adaptive_entrain_count}/{self.ADAPTIVE_ENTRAIN_GRACE_BREATHS} "
                    f"grace breaths discarded at {self.adaptive_current_rate:.2f} bpm"
                )
                return

            # Record HRV sample for current dwell
            maxmin = self._get_latest_maxmin()
            if maxmin is not None:
                self.adaptive_hrv_samples.append(maxmin)
                self.adaptive_dwell_count += 1

            # Check if we've dwelled enough
            if self.adaptive_dwell_count >= self.ADAPTIVE_DWELL_BREATHS:
                if len(self.adaptive_hrv_samples) >= self.ADAPTIVE_DWELL_BREATHS:
                    if protocol["mode"] == "adaptive_explore":
                        self._adaptive_explore_step()
                    else:
                        self._adaptive_refine_step()

    def get_current_breathing_rate(self, manual_rate=None):
        """
        Get the current breathing rate based on active protocol.

        Args:
            manual_rate: Manual rate from slider (used if protocol is Manual
                         or to set initial rate for Adaptive Refine)

        Returns:
            Current breathing rate in bpm
        """
        protocol = self.protocols[self.current_protocol]

        # Manual / Timed Manual mode - use slider value
        if protocol["mode"] in ("manual", "timed_manual"):
            return manual_rate if manual_rate is not None else 6.0

        # Fixed mode - constant rate
        if protocol["mode"] == "fixed":
            return protocol["start_rate"]

        # Automatic mode (Fisher & Lehrer) - discrete per-breath rate changes
        if protocol["mode"] == "automatic" and self.is_running:
            if self.current_breath_period_ms > 0:
                return 60000.0 / self.current_breath_period_ms
            else:
                return protocol["start_rate"]

        # Adaptive modes
        if protocol["mode"] in ("adaptive_explore", "adaptive_refine") and self.is_running:
            # Adaptive Refine: capture slider rate on first call
            if protocol["mode"] == "adaptive_refine" and not self.adaptive_initial_rate_set:
                start_rate = manual_rate if manual_rate is not None else 5.0
                self.adaptive_initial_rate_set = True
                self._init_refine_coarse_points(start_rate)
                self.logger.info(f"Adaptive Refine initialized around {start_rate:.2f} bpm")

            if self.current_breath_period_ms > 0:
                return 60000.0 / self.current_breath_period_ms
            else:
                return self.ADAPTIVE_EXPLORE_START_RATE

        # Default
        return protocol.get("start_rate") or 6.0

    def get_session_info(self):
        """Get information about current session"""
        if not self.is_running or self.session_start_time is None:
            return {
                "elapsed": 0,
                "remaining": 0,
                "progress": 0,
                "is_complete": False
            }

        protocol = self.protocols[self.current_protocol]
        elapsed = time.time() - self.session_start_time

        if protocol["duration"] is None:
            return {
                "elapsed": elapsed,
                "remaining": None,
                "progress": 0,
                "is_complete": False
            }

        duration = protocol["duration"]
        remaining = max(0, duration - elapsed)
        progress = min(100, (elapsed / duration) * 100)
        is_complete = elapsed >= duration

        return {
            "elapsed": elapsed,
            "remaining": remaining,
            "progress": progress,
            "is_complete": is_complete
        }

    def set_timed_duration(self, seconds):
        """Set duration for Timed_Manual protocol"""
        self.protocols["Timed_Manual"]["duration"] = max(1, int(seconds))

    def is_fisher_lehrer_protocol(self):
        """Check if current protocol is Fisher & Lehrer"""
        return self.current_protocol == "Fisher_Lehrer"

    def is_adaptive_protocol(self):
        """Check if current protocol is an adaptive mode"""
        return self.current_protocol in ("Adaptive_Explore", "Adaptive_Refine")

    def is_timed_manual_protocol(self):
        """Check if current protocol is Timed Manual"""
        return self.current_protocol == "Timed_Manual"
