"""
ghost_lidar.py — Synthetic LiDAR Data Generator (The "Ghost Stream")

Replaces physical $50K LiDAR hardware with a software-defined sensor simulator.
Generates a continuously updating Digital Shadow (barge_state.json) that feeds
the CesiumJS + React visual dashboard.

Architecture: State-First (Blueprint v4.0 Directive 5)
- Treats the barge as a JSON State Object (Eclipse Ditto style)
- Writes to state/barge_state.json at 1Hz
- No terminal output — runs silently as background process
- Dashboard reads the JSON file for real-time visualization

Authority: Chief Dre, Sovereign Intent Originator (Level 0)
"""

import json
import math
import os
import random
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional


# ============================================================
# DATA STRUCTURES — Blueprint v4.0 Appendix (Authoritative)
# Do NOT modify keys without Level 0 approval.
# ============================================================

@dataclass
class DraftReadings:
    """4-point draft sensor readings in feet."""
    fore: float = 9.80
    aft: float = 9.90
    port: float = 9.85
    starboard: float = 9.85
    mean: float = 9.85
    unit: str = "ft"

    def compute_mean(self):
        """Simpson's rule: (fore + 6*mid + aft) / 8"""
        mid = (self.port + self.starboard) / 2
        self.mean = round((self.fore + 6 * mid + self.aft) / 8, 3)


@dataclass
class StabilityMetrics:
    """Vessel stability state."""
    trim: float = 0.0        # meters, positive = bow heavy
    heel: float = 0.0        # degrees, negative = port list
    displacement: float = 1800.0  # metric tons
    gm: float = 3.65         # metacentric height (m)
    status: str = "NOMINAL"  # NOMINAL | CAUTION | CRITICAL | CRITICAL_STOP


@dataclass
class CraneSignals:
    """Crane operational state with signal and G-codes."""
    load_weight: float = 0.0
    max_capacity: float = 3200.0
    boom_angle: float = 0.0
    slew_bearing: float = 0.0
    hook_height: float = 20.0
    status: str = "IDLE"           # IDLE | POSITIONING | LOADING | E_STOP
    signal_code: str = "SIG-000"   # SIG-000 (IDLE) through SIG-910 (OVERLOAD)
    g_code: str = "G00"            # G00=rapid, G01=linear, M00=emergency halt


@dataclass
class WorkflowState:
    """6-phase barge drafting workflow FSM."""
    current_phase: str = "PRE-SURVEY"
    phase_index: int = 0
    elapsed_seconds: float = 0.0
    target_seconds: float = 900.0  # 15 min total
    phases: list = field(default_factory=lambda: [
        "PRE-SURVEY", "BALLAST-ADJ", "CRANE-POS",
        "CARGO-LOAD", "TRIM-CORR", "FINAL-SURV"
    ])


@dataclass
class Alerts:
    """Safety alert flags."""
    man_overboard: bool = False
    list_warning: bool = False
    overload_warning: bool = False
    trim_warning: bool = False
    heat_signature_anomaly: bool = False


@dataclass
class GhostLidarMeta:
    """Ghost LiDAR scan metadata."""
    point_count: int = 6000
    scan_pattern: str = "lawnmower"
    chaos_mode: bool = False
    scan_rate_hz: float = 1.0


@dataclass
class Governance:
    """FREQ LAW governance state."""
    freq_law: str = "COMPLIANT"      # COMPLIANT | EMERGENCY HALT
    veto_status: str = "CLEAR"       # CLEAR | SAFETY VETO
    consensus: str = "3/3 APPROVED"  # k=3 quorum


@dataclass
class BargeState:
    """Complete Digital Shadow — the single source of truth."""
    timestamp: float = 0.0
    barge_id: str = "BARGE-GOM-2026-001"
    barge_name: str = "Gulf Runner 1"
    location: dict = field(default_factory=lambda: {"lat": 29.31, "lon": -94.79})
    draft: DraftReadings = field(default_factory=DraftReadings)
    stability: StabilityMetrics = field(default_factory=StabilityMetrics)
    crane: CraneSignals = field(default_factory=CraneSignals)
    workflow: WorkflowState = field(default_factory=WorkflowState)
    alerts: Alerts = field(default_factory=Alerts)
    ghost_lidar: GhostLidarMeta = field(default_factory=GhostLidarMeta)
    governance: Governance = field(default_factory=Governance)

    def to_dict(self):
        return asdict(self)

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent)


# ============================================================
# GHOST LIDAR ENGINE — Synthetic Data Generator
# ============================================================

class GhostLidarEngine:
    """
    Generates synthetic barge sensor data that simulates realistic
    maritime operations. Replaces $50K physical LiDAR hardware.

    Usage:
        engine = GhostLidarEngine()
        engine.run()  # Runs forever, writes state/barge_state.json at 1Hz

        # Or with man overboard trigger:
        engine.trigger_man_overboard()
    """

    # Phase durations in seconds (real simulation timing)
    PHASE_DURATIONS = {
        "PRE-SURVEY": 120,   # 2 min
        "BALLAST-ADJ": 150,  # 2.5 min
        "CRANE-POS": 90,     # 1.5 min
        "CARGO-LOAD": 300,   # 5 min
        "TRIM-CORR": 120,    # 2 min
        "FINAL-SURV": 120,   # 2 min
    }  # Total: ~15 min (900s)

    def __init__(self, output_path: Optional[str] = None, demo_speed: float = 1.0):
        """
        Args:
            output_path: Path to write barge_state.json. Defaults to state/barge_state.json.
            demo_speed: Speed multiplier. 1.0 = real time, 10.0 = 10x faster.
        """
        self.state = BargeState()
        self.demo_speed = demo_speed
        self._phase_start_time = time.time()
        self._sim_start_time = time.time()
        self._mob_active = False
        self._mob_start_time = 0.0
        self._running = False

        # Output path
        if output_path:
            self.output_path = Path(output_path)
        else:
            self.output_path = Path(__file__).parent.parent.parent.parent / "state" / "barge_state.json"
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def _noise(self, base: float, amplitude: float) -> float:
        """Add realistic sensor noise."""
        return base + (random.random() - 0.5) * amplitude

    def _wave_motion(self, t: float, period: float = 8.0, amp: float = 0.3) -> float:
        """Simulate gentle wave-induced motion."""
        return amp * math.sin(2 * math.pi * t / period)

    def _update_phase(self):
        """Progress through 6-phase workflow."""
        elapsed = (time.time() - self._phase_start_time) * self.demo_speed
        phase = self.state.workflow.current_phase
        duration = self.PHASE_DURATIONS.get(phase, 120)

        self.state.workflow.elapsed_seconds = round(elapsed, 1)

        if elapsed >= duration:
            idx = self.state.workflow.phase_index
            idx = (idx + 1) % 6
            self.state.workflow.phase_index = idx
            self.state.workflow.current_phase = self.state.workflow.phases[idx]
            self._phase_start_time = time.time()
            if idx == 0:
                self._sim_start_time = time.time()

    def _update_sensors(self):
        """Update all sensor readings based on current phase."""
        phase = self.state.workflow.current_phase
        t_phase = (time.time() - self._phase_start_time) * self.demo_speed
        duration = self.PHASE_DURATIONS.get(phase, 120)
        progress = min(t_phase / duration, 1.0)  # 0.0 to 1.0
        t_global = time.time() - self._sim_start_time
        wave = self._wave_motion(t_global)

        d = self.state.draft
        s = self.state.stability
        c = self.state.crane

        if phase == "PRE-SURVEY":
            # Light draft, minimal trim, LiDAR scanning
            d.fore = self._noise(9.80, 0.04) + wave * 0.02
            d.aft = self._noise(9.90, 0.04) + wave * 0.02
            d.port = self._noise(9.85, 0.03)
            d.starboard = self._noise(9.85, 0.03)
            c.status = "IDLE"
            c.signal_code = "SIG-000"
            c.g_code = "G00"
            c.load_weight = 0
            c.boom_angle = 0
            s.trim = self._noise(0.08, 0.02) + wave * 0.01
            s.heel = self._noise(0.0, 0.3) + wave * 0.1
            s.displacement = self._noise(1800, 10)

        elif phase == "BALLAST-ADJ":
            # Ballast tanks filling, trim correcting
            d.fore = self._noise(10.00 + progress * 0.1, 0.03)
            d.aft = self._noise(10.05 - progress * 0.05, 0.03)
            d.port = self._noise(10.02 + progress * 0.05, 0.03)
            d.starboard = self._noise(10.02 + progress * 0.05, 0.03)
            s.trim = self._noise(0.08 * (1 - progress), 0.02)
            s.heel = self._noise(1.5 * (1 - progress), 0.2) + wave * 0.05
            s.displacement = self._noise(1850 + progress * 50, 10)
            c.status = "IDLE"
            c.signal_code = "SIG-000"
            c.g_code = "G00"

        elif phase == "CRANE-POS":
            # Crane moving to position
            c.boom_angle = round(15 + progress * 27.3, 1)
            c.slew_bearing = round(progress * 195.7, 1)
            c.hook_height = round(20 - progress * 3.8, 1)
            c.status = "POSITIONING"
            c.signal_code = "SIG-100"
            c.g_code = f"G01 X{c.slew_bearing:.1f} Y{c.boom_angle:.1f}"
            s.trim = self._noise(0.02, 0.01)
            s.heel = self._noise(-0.5 * progress, 0.2)

        elif phase == "CARGO-LOAD":
            # Loading cargo — draft increases, trim by stern
            load = round(progress * 1800)
            c.load_weight = load
            c.boom_angle = self._noise(42.3, 1.0)
            c.slew_bearing = self._noise(195.7, 2.0)
            c.hook_height = self._noise(16.2, 0.3)
            c.status = "LOADING"
            c.signal_code = "SIG-LOAD"
            c.g_code = f"G01 X{c.slew_bearing:.1f} Y{c.boom_angle:.1f}"
            d.fore = self._noise(10.10 + progress * 0.35, 0.03) + wave * 0.02
            d.aft = self._noise(10.15 + progress * 0.50, 0.03) + wave * 0.02
            d.port = self._noise(10.12 + progress * 0.40, 0.03)
            d.starboard = self._noise(10.12 + progress * 0.40, 0.03)
            s.trim = self._noise(0.15 + progress * 0.35, 0.03)
            s.heel = self._noise(-0.5 - progress * 1.5, 0.3) + wave * 0.1
            s.displacement = self._noise(1900 + progress * 1300, 15)
            s.gm = self._noise(3.65 - progress * 0.3, 0.05)

        elif phase == "TRIM-CORR":
            # Trim correction — stabilizing
            c.status = "IDLE"
            c.signal_code = "SIG-000"
            c.g_code = "G00"
            c.load_weight = 0
            s.trim = self._noise(0.50 * (1 - progress), 0.02)
            s.heel = self._noise(-2.0 * (1 - progress), 0.2) + wave * 0.05
            s.displacement = self._noise(3200, 10)
            s.gm = self._noise(3.35 + progress * 0.30, 0.03)
            d.fore = self._noise(10.45 + progress * 0.10, 0.02)
            d.aft = self._noise(10.65 - progress * 0.10, 0.02)
            d.port = self._noise(10.55, 0.02)
            d.starboard = self._noise(10.55, 0.02)

        elif phase == "FINAL-SURV":
            # Final survey — stable readings
            d.fore = self._noise(10.55, 0.01) + wave * 0.005
            d.aft = self._noise(10.55, 0.01) + wave * 0.005
            d.port = self._noise(10.55, 0.01)
            d.starboard = self._noise(10.53, 0.01)
            c.status = "IDLE"
            c.signal_code = "SIG-000"
            c.g_code = "G00"
            s.trim = self._noise(0.02, 0.01)
            s.heel = self._noise(0.0, 0.1) + wave * 0.03
            s.displacement = self._noise(3200, 5)
            s.gm = self._noise(3.65, 0.02)
            self.state.governance.freq_law = "COMPLIANT"
            self.state.governance.consensus = "3/3 APPROVED"

        # Compute mean draft (Simpson's rule)
        d.compute_mean()

        # Round all floats for clean output
        d.fore = round(d.fore, 3)
        d.aft = round(d.aft, 3)
        d.port = round(d.port, 3)
        d.starboard = round(d.starboard, 3)
        s.trim = round(s.trim, 3)
        s.heel = round(s.heel, 3)
        s.displacement = round(s.displacement, 1)
        s.gm = round(s.gm, 3)
        c.boom_angle = round(c.boom_angle, 1)
        c.slew_bearing = round(c.slew_bearing, 1)
        c.hook_height = round(c.hook_height, 1)

    def _update_stability_status(self):
        """Evaluate stability thresholds and set alerts."""
        s = self.state.stability
        a = self.state.alerts

        if self._mob_active:
            return  # MOB overrides normal status

        abs_heel = abs(s.heel)
        abs_trim = abs(s.trim)

        if abs_heel > 5.0 or s.gm < 0.5:
            s.status = "CRITICAL"
        elif abs_heel > 2.0 or abs_trim > 0.8 or s.gm < 1.5:
            s.status = "CAUTION"
        else:
            s.status = "NOMINAL"

        a.list_warning = abs_heel > 3.0
        a.trim_warning = abs_trim > 1.0
        a.overload_warning = self.state.crane.load_weight > self.state.crane.max_capacity * 0.9

    def trigger_man_overboard(self):
        """
        Inject Man Overboard emergency — the "Chaos Mode" safety trigger.

        Injects heat signature anomaly, activates CGE SAFETY VETO,
        sets crane to emergency halt (M00), and destabilizes barge readings.
        Auto-recovers after 10 seconds.
        """
        self._mob_active = True
        self._mob_start_time = time.time()
        self.state.alerts.man_overboard = True
        self.state.alerts.heat_signature_anomaly = True
        self.state.ghost_lidar.chaos_mode = True
        self.state.stability.status = "CRITICAL_STOP"
        self.state.governance.freq_law = "EMERGENCY HALT"
        self.state.governance.veto_status = "SAFETY VETO"
        self.state.crane.status = "E_STOP"
        self.state.crane.signal_code = "SIG-910"
        self.state.crane.g_code = "M00"

    def _update_mob(self):
        """Handle MOB chaos mode — random disturbances for 10 seconds."""
        if not self._mob_active:
            return

        elapsed = time.time() - self._mob_start_time

        if elapsed > 10.0:
            # Auto-recover
            self._mob_active = False
            self.state.alerts.man_overboard = False
            self.state.alerts.heat_signature_anomaly = False
            self.state.ghost_lidar.chaos_mode = False
            self.state.stability.status = "NOMINAL"
            self.state.stability.heel = 0.0
            self.state.stability.trim = 0.02
            self.state.governance.freq_law = "COMPLIANT"
            self.state.governance.veto_status = "CLEAR"
            self.state.crane.status = "IDLE"
            self.state.crane.signal_code = "SIG-000"
            self.state.crane.g_code = "G00"
            return

        # Chaotic disturbances
        self.state.stability.heel = round(-8 + random.random() * 16, 3)
        self.state.stability.trim = round(-1 + random.random() * 2, 3)
        self.state.crane.boom_angle = round(random.random() * 60, 1)
        self.state.draft.fore += (random.random() - 0.5) * 0.5
        self.state.draft.aft += (random.random() - 0.5) * 0.5
        self.state.draft.compute_mean()

    def _write_state(self):
        """Write current state to barge_state.json (atomic write)."""
        self.state.timestamp = round(time.time(), 3)
        data = self.state.to_json()

        # Atomic write: write to temp file then rename
        tmp_path = self.output_path.with_suffix('.tmp')
        tmp_path.write_text(data)
        tmp_path.rename(self.output_path)

    def tick(self):
        """Single simulation tick — call at 1Hz."""
        if not self._mob_active:
            self._update_phase()
            self._update_sensors()
        self._update_mob()
        self._update_stability_status()
        self._write_state()

    def run(self, duration: Optional[float] = None):
        """
        Run the ghost stream continuously.

        Args:
            duration: Run for N seconds then stop. None = run forever.
        """
        self._running = True
        self._sim_start_time = time.time()
        self._phase_start_time = time.time()
        start = time.time()

        while self._running:
            self.tick()
            if duration and (time.time() - start) >= duration:
                break
            time.sleep(1.0 / self.state.ghost_lidar.scan_rate_hz)

    def stop(self):
        """Stop the run loop."""
        self._running = False


# ============================================================
# CLI — For direct execution
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ghost LiDAR — Synthetic Barge Data Generator")
    parser.add_argument("--output", type=str, default=None, help="Output path for barge_state.json")
    parser.add_argument("--speed", type=float, default=1.0, help="Demo speed multiplier (1.0=real, 10.0=fast)")
    parser.add_argument("--duration", type=float, default=None, help="Run for N seconds then stop")
    parser.add_argument("--mob", action="store_true", help="Trigger Man Overboard after 5 seconds")
    args = parser.parse_args()

    engine = GhostLidarEngine(output_path=args.output, demo_speed=args.speed)

    if args.mob:
        # Schedule MOB trigger after 5 seconds
        import threading
        timer = threading.Timer(5.0, engine.trigger_man_overboard)
        timer.start()

    engine.run(duration=args.duration)
