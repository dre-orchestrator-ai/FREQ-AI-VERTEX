"""
Telemetry Simulator for Lattice Core

Generates mock sensor data for barge-under-load simulations.
Designed for Google Cloud REQ demonstration.

Simulation Modes:
    - STATIC: Fixed values for testing
    - LOADING: Gradual cargo loading
    - TRANSIT: In-transit with environmental variation
    - STRESS: High-load stability testing
"""

import json
import math
import random
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from enum import Enum

from .bigquery_bridge import (
    BigQueryBridge,
    TelemetryRecord,
    BargeState,
    MeasurementType,
    StabilityStatus,
)


class SimulationMode(Enum):
    """Simulation modes for telemetry generation."""
    STATIC = "STATIC"           # Fixed values
    LOADING = "LOADING"         # Cargo loading sequence
    TRANSIT = "TRANSIT"         # In-transit operation
    STRESS = "STRESS"           # High-load stress test
    UNLOADING = "UNLOADING"     # Cargo unloading sequence


@dataclass
class SimulationConfig:
    """
    Configuration for telemetry simulation.

    Attributes:
        mode: Simulation mode
        barge_id: Target barge identifier
        duration_seconds: Total simulation duration
        update_interval_ms: Milliseconds between updates
        noise_factor: Random variation factor (0.0 - 1.0)
        target_cargo_tons: Target cargo load
        loading_rate_tons_per_min: Cargo loading rate
    """
    mode: SimulationMode = SimulationMode.TRANSIT
    barge_id: str = "BARGE-DELTA-001"
    vessel_name: str = "Delta Pioneer"
    duration_seconds: int = 600  # 10 minutes
    update_interval_ms: int = 1000  # 1 second
    noise_factor: float = 0.02
    target_cargo_tons: float = 1800.0
    loading_rate_tons_per_min: float = 50.0

    # Vessel specifications
    max_draft_m: float = 3.8
    max_cargo_tons: float = 2200.0
    light_draft_m: float = 1.8
    length_m: float = 76.2
    beam_m: float = 10.7

    # Environmental baseline
    water_temp_c: float = 18.5
    salinity_ppt: float = 32.0
    latitude: float = 29.7604
    longitude: float = -95.3698  # Houston

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "barge_id": self.barge_id,
            "vessel_name": self.vessel_name,
            "duration_seconds": self.duration_seconds,
            "update_interval_ms": self.update_interval_ms,
            "noise_factor": self.noise_factor,
            "target_cargo_tons": self.target_cargo_tons,
        }


class TelemetrySimulator:
    """
    Telemetry Simulator for Lattice Core demonstrations.

    Generates realistic barge telemetry data including:
    - Draft readings (forward, midship, aft)
    - Trim and list calculations
    - Cargo weight progression
    - Environmental variations

    Usage:
        config = SimulationConfig(
            mode=SimulationMode.LOADING,
            barge_id="BARGE-DELTA-001",
            duration_seconds=600,
        )

        simulator = TelemetrySimulator(config)
        simulator.set_bridge(bigquery_bridge)

        # Run simulation
        simulator.start()

        # Check status
        print(simulator.get_status())

        # Stop when done
        simulator.stop()
    """

    def __init__(self, config: SimulationConfig):
        """
        Initialize simulator with configuration.

        Args:
            config: SimulationConfig instance
        """
        self.config = config
        self._bridge: Optional[BigQueryBridge] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._start_time: Optional[float] = None
        self._tick_count = 0
        self._current_state: Optional[BargeState] = None
        self._callbacks: Dict[str, List[Callable]] = {
            "on_tick": [],
            "on_state_update": [],
            "on_complete": [],
        }

        # Initialize state
        self._init_state()

    def _init_state(self) -> None:
        """Initialize the barge state."""
        cfg = self.config

        # Initial draft based on light ship
        initial_draft = cfg.light_draft_m

        self._current_state = BargeState(
            barge_id=cfg.barge_id,
            vessel_name=cfg.vessel_name,
            forward_draft_m=initial_draft - 0.05,
            midship_draft_m=initial_draft,
            aft_draft_m=initial_draft + 0.05,
            trim_m=-0.1,
            list_deg=0.0,
            cargo_tons=0.0,
            cargo_type="EMPTY",
            water_temp_c=cfg.water_temp_c,
            salinity_ppt=cfg.salinity_ppt,
            latitude=cfg.latitude,
            longitude=cfg.longitude,
            stability_status=StabilityStatus.STABLE,
            operational_mode="IDLE",
            max_draft_m=cfg.max_draft_m,
            max_cargo_tons=cfg.max_cargo_tons,
        )

    def set_bridge(self, bridge: BigQueryBridge) -> None:
        """Set the BigQuery bridge for data streaming."""
        self._bridge = bridge

    def register_callback(self, event: str, callback: Callable) -> None:
        """Register callback for simulator events."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _emit(self, event: str, *args, **kwargs) -> None:
        """Emit event to registered callbacks."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception:
                pass

    def start(self) -> None:
        """Start the simulation."""
        if self._running:
            return

        self._running = True
        self._start_time = time.time()
        self._tick_count = 0

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the simulation."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _run_loop(self) -> None:
        """Main simulation loop."""
        interval = self.config.update_interval_ms / 1000.0

        while self._running:
            elapsed = time.time() - self._start_time

            # Check duration
            if elapsed >= self.config.duration_seconds:
                self._running = False
                self._emit("on_complete", self._current_state)
                break

            # Update state
            self._tick()

            # Sleep for interval
            time.sleep(interval)

    def _tick(self) -> None:
        """Process a single simulation tick."""
        self._tick_count += 1
        elapsed = time.time() - self._start_time
        progress = elapsed / self.config.duration_seconds

        # Update state based on mode
        if self.config.mode == SimulationMode.LOADING:
            self._update_loading_state(progress)
        elif self.config.mode == SimulationMode.UNLOADING:
            self._update_unloading_state(progress)
        elif self.config.mode == SimulationMode.TRANSIT:
            self._update_transit_state(progress)
        elif self.config.mode == SimulationMode.STRESS:
            self._update_stress_state(progress)
        else:  # STATIC
            self._add_noise()

        # Update timestamp
        self._current_state.timestamp = datetime.utcnow().isoformat() + "Z"

        # Compute stability
        self._current_state.stability_status = self._current_state.compute_stability_status()

        # Stream to bridge
        if self._bridge:
            self._bridge.update_barge_state(self._current_state)
            self._stream_telemetry()

        # Emit callbacks
        self._emit("on_tick", self._tick_count, self._current_state)
        self._emit("on_state_update", self._current_state)

    def _update_loading_state(self, progress: float) -> None:
        """Update state for loading simulation."""
        cfg = self.config
        state = self._current_state

        # Calculate target cargo at this point
        target_cargo = min(cfg.target_cargo_tons * progress, cfg.target_cargo_tons)

        # Calculate draft increase per ton of cargo
        draft_per_ton = (cfg.max_draft_m - cfg.light_draft_m) / cfg.max_cargo_tons

        # Update cargo and draft
        state.cargo_tons = target_cargo
        state.cargo_type = "BULK_CARGO" if target_cargo > 0 else "EMPTY"

        # Calculate new drafts
        draft_increase = target_cargo * draft_per_ton
        base_draft = cfg.light_draft_m + draft_increase

        # Add realistic trim variation during loading
        loading_trim = -0.1 - (progress * 0.08)  # Stern heavier during loading

        state.midship_draft_m = base_draft + self._noise(0.01)
        state.forward_draft_m = base_draft - (loading_trim / 2) + self._noise(0.01)
        state.aft_draft_m = base_draft + (loading_trim / 2) + self._noise(0.01)
        state.trim_m = state.forward_draft_m - state.aft_draft_m

        # List variation during loading
        state.list_deg = self._noise(0.3)

        # Operational mode
        if progress < 0.95:
            state.operational_mode = "LOADING"
        else:
            state.operational_mode = "LOADED"

    def _update_unloading_state(self, progress: float) -> None:
        """Update state for unloading simulation."""
        cfg = self.config
        state = self._current_state

        # Reverse of loading
        remaining_cargo = cfg.target_cargo_tons * (1 - progress)

        draft_per_ton = (cfg.max_draft_m - cfg.light_draft_m) / cfg.max_cargo_tons
        draft_increase = remaining_cargo * draft_per_ton
        base_draft = cfg.light_draft_m + draft_increase

        state.cargo_tons = remaining_cargo
        state.cargo_type = "BULK_CARGO" if remaining_cargo > 100 else "EMPTY"

        # Trim shifts forward during unloading (bow heavier)
        unloading_trim = -0.18 + (progress * 0.1)

        state.midship_draft_m = base_draft + self._noise(0.01)
        state.forward_draft_m = base_draft - (unloading_trim / 2) + self._noise(0.01)
        state.aft_draft_m = base_draft + (unloading_trim / 2) + self._noise(0.01)
        state.trim_m = state.forward_draft_m - state.aft_draft_m

        state.list_deg = self._noise(0.4)
        state.operational_mode = "UNLOADING"

    def _update_transit_state(self, progress: float) -> None:
        """Update state for transit simulation."""
        state = self._current_state

        # Wave-induced motion
        wave_period = 8.0  # seconds
        wave_amplitude_draft = 0.03
        wave_amplitude_list = 0.8

        elapsed = time.time() - self._start_time
        wave_phase = (elapsed / wave_period) * 2 * math.pi

        # Draft oscillation
        draft_variation = wave_amplitude_draft * math.sin(wave_phase)

        state.midship_draft_m += draft_variation
        state.forward_draft_m = state.midship_draft_m + 0.05 * math.sin(wave_phase + 0.5)
        state.aft_draft_m = state.midship_draft_m - 0.05 * math.sin(wave_phase + 0.5)
        state.trim_m = state.forward_draft_m - state.aft_draft_m

        # List oscillation (roll)
        state.list_deg = wave_amplitude_list * math.sin(wave_phase * 1.3)

        # Position update (slow movement)
        state.latitude += 0.0001 * math.sin(progress * math.pi)
        state.longitude -= 0.0002 * progress

        # Environmental variation
        state.water_temp_c = self.config.water_temp_c + self._noise(0.3)
        state.salinity_ppt = self.config.salinity_ppt + self._noise(0.5)

        state.operational_mode = "IN_TRANSIT"

    def _update_stress_state(self, progress: float) -> None:
        """Update state for stress test simulation."""
        cfg = self.config
        state = self._current_state

        # Ramp up to near-maximum load
        stress_cargo = cfg.max_cargo_tons * (0.85 + progress * 0.12)

        draft_per_ton = (cfg.max_draft_m - cfg.light_draft_m) / cfg.max_cargo_tons
        draft_increase = stress_cargo * draft_per_ton
        base_draft = cfg.light_draft_m + draft_increase

        state.cargo_tons = min(stress_cargo, cfg.max_cargo_tons * 0.98)
        state.cargo_type = "HEAVY_CARGO"

        # Increasing trim and list to simulate stress
        stress_trim = -0.25 - (progress * 0.15)
        stress_list = 0.5 + (progress * 1.0) + self._noise(0.3)

        state.midship_draft_m = base_draft + self._noise(0.02)
        state.forward_draft_m = base_draft - (stress_trim / 2) + self._noise(0.02)
        state.aft_draft_m = base_draft + (stress_trim / 2) + self._noise(0.02)
        state.trim_m = state.forward_draft_m - state.aft_draft_m
        state.list_deg = stress_list

        state.operational_mode = "STRESS_TEST"

    def _add_noise(self) -> None:
        """Add random noise to static state."""
        state = self._current_state
        state.midship_draft_m += self._noise(0.005)
        state.forward_draft_m += self._noise(0.005)
        state.aft_draft_m += self._noise(0.005)
        state.list_deg += self._noise(0.1)

    def _noise(self, amplitude: float) -> float:
        """Generate random noise."""
        return (random.random() - 0.5) * 2 * amplitude * self.config.noise_factor

    def _stream_telemetry(self) -> None:
        """Stream individual telemetry records to bridge."""
        if not self._bridge:
            return

        state = self._current_state
        timestamp = state.timestamp

        records = [
            TelemetryRecord(
                barge_id=state.barge_id,
                timestamp=timestamp,
                sensor_id=f"SENSOR-FWDRAFT-{state.barge_id}",
                measurement_type=MeasurementType.DRAFT_FORWARD,
                value=state.forward_draft_m,
                unit="meters",
                quality_score=0.995 + random.random() * 0.005,
            ),
            TelemetryRecord(
                barge_id=state.barge_id,
                timestamp=timestamp,
                sensor_id=f"SENSOR-MIDDRAFT-{state.barge_id}",
                measurement_type=MeasurementType.DRAFT_MIDSHIP,
                value=state.midship_draft_m,
                unit="meters",
                quality_score=0.995 + random.random() * 0.005,
            ),
            TelemetryRecord(
                barge_id=state.barge_id,
                timestamp=timestamp,
                sensor_id=f"SENSOR-AFTDRAFT-{state.barge_id}",
                measurement_type=MeasurementType.DRAFT_AFT,
                value=state.aft_draft_m,
                unit="meters",
                quality_score=0.995 + random.random() * 0.005,
            ),
            TelemetryRecord(
                barge_id=state.barge_id,
                timestamp=timestamp,
                sensor_id=f"SENSOR-INCLINE-{state.barge_id}",
                measurement_type=MeasurementType.LIST,
                value=state.list_deg,
                unit="degrees",
                quality_score=0.998,
            ),
            TelemetryRecord(
                barge_id=state.barge_id,
                timestamp=timestamp,
                sensor_id=f"SENSOR-LOAD-{state.barge_id}",
                measurement_type=MeasurementType.CARGO_WEIGHT,
                value=state.cargo_tons,
                unit="tons",
                quality_score=0.992,
            ),
        ]

        self._bridge.stream_batch(records)

    def get_status(self) -> Dict[str, Any]:
        """Get current simulation status."""
        elapsed = 0.0
        remaining = self.config.duration_seconds

        if self._start_time:
            elapsed = time.time() - self._start_time
            remaining = max(0, self.config.duration_seconds - elapsed)

        return {
            "running": self._running,
            "mode": self.config.mode.value,
            "barge_id": self.config.barge_id,
            "tick_count": self._tick_count,
            "elapsed_seconds": round(elapsed, 1),
            "remaining_seconds": round(remaining, 1),
            "progress_percent": round((elapsed / self.config.duration_seconds) * 100, 1),
            "current_state": self._current_state.to_bigquery_row() if self._current_state else None,
        }

    def get_current_state(self) -> Optional[BargeState]:
        """Get current barge state."""
        return self._current_state

    def get_telemetry_json(self) -> str:
        """Get current state as JSON for streaming."""
        if not self._current_state:
            return "{}"
        return self._current_state.to_telemetry_json()


def create_demo_simulation(
    barge_id: str = "BARGE-DELTA-001",
    mode: SimulationMode = SimulationMode.LOADING,
    duration_minutes: int = 10
) -> TelemetrySimulator:
    """
    Create a pre-configured simulation for REQ demo.

    Args:
        barge_id: Barge identifier
        mode: Simulation mode
        duration_minutes: Duration in minutes

    Returns:
        Configured TelemetrySimulator
    """
    config = SimulationConfig(
        mode=mode,
        barge_id=barge_id,
        vessel_name="Delta Pioneer",
        duration_seconds=duration_minutes * 60,
        update_interval_ms=1000,
        noise_factor=0.02,
        target_cargo_tons=1800.0,
        max_draft_m=3.8,
        max_cargo_tons=2200.0,
        light_draft_m=1.8,
    )

    return TelemetrySimulator(config)
