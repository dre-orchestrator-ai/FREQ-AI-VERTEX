"""
Simulation Runner for Lattice Core

Main entry point for running the Lattice Core simulation for
Google Cloud REQ demonstration.

Features:
- 10-minute autonomous simulation
- Real-time telemetry streaming to BigQuery
- JSON output for dashboard integration
- Console status reporting

Usage:
    python -m sol.lattice_core.simulation_runner

    Or with custom configuration:
    python -m sol.lattice_core.simulation_runner --mode LOADING --duration 600
"""

import argparse
import json
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

from .bigquery_bridge import BigQueryBridge, BargeState, StabilityStatus
from .supply_chain_twin import SupplyChainTwinClient, EntityType, create_barge_twin_from_legacy
from .telemetry_simulator import TelemetrySimulator, SimulationConfig, SimulationMode
from .lattice_status import LatticeStatus


class LatticeCoreDemoRunner:
    """
    Main runner for Lattice Core demonstration.

    Orchestrates:
    - BigQuery bridge initialization
    - Supply Chain Twin setup
    - Telemetry simulation
    - Dashboard data streaming
    """

    def __init__(
        self,
        project_id: str = "",
        mode: SimulationMode = SimulationMode.LOADING,
        duration_seconds: int = 600,
        dashboard_port: int = 8080
    ):
        """
        Initialize the demo runner.

        Args:
            project_id: GCP project ID
            mode: Simulation mode
            duration_seconds: Total simulation duration (default 10 minutes)
            dashboard_port: Port for dashboard server
        """
        self.project_id = project_id
        self.mode = mode
        self.duration_seconds = duration_seconds
        self.dashboard_port = dashboard_port

        # Initialize components
        self.bridge = BigQueryBridge(project_id=project_id)
        self.twin_client = SupplyChainTwinClient(project_id=project_id)
        self.status = LatticeStatus()
        self.simulator = None

        self._running = False
        self._start_time = None
        self._dashboard_server = None

    def setup(self) -> None:
        """Set up all components for the demo."""
        print("\n" + "=" * 60)
        print("  LATTICE CORE - Maritime Digital Mirror")
        print("  Google Cloud Supply Chain Twin Demo")
        print("=" * 60 + "\n")

        # Load legacy configuration
        print("[INIT] Loading legacy fleet configuration...")
        legacy_config = self._load_legacy_config()

        # Set up Supply Chain Twin entities
        print("[INIT] Creating Supply Chain Twin entities...")
        self._setup_twin_entities(legacy_config)

        # Configure simulation
        print(f"[INIT] Configuring simulation: {self.mode.value}")
        self._setup_simulation()

        # Update system status
        self.status.update_system_status(
            bigquery=True,
            supply_chain_twin=True,
            iot_core=True,
            simulation=True
        )

        print("[INIT] Setup complete.\n")

    def _load_legacy_config(self) -> dict:
        """Load legacy hull displacement configuration."""
        config_path = Path(__file__).parent.parent.parent.parent / "ref_legacy" / "hull_displacement_config.json"

        if config_path.exists():
            with open(config_path, "r") as f:
                return json.load(f)

        # Return default config if file not found
        return {
            "fleet_registry": {
                "BARGE-DELTA-001": {
                    "vessel_name": "Delta Pioneer",
                    "vessel_type": "CARGO_BARGE",
                    "dimensions": {
                        "length_m": 76.2,
                        "beam_m": 10.7,
                        "max_draft_m": 3.8
                    },
                    "displacement": {
                        "max_cargo_tons": 2200
                    }
                }
            }
        }

    def _setup_twin_entities(self, legacy_config: dict) -> None:
        """Create Supply Chain Twin entities from legacy config."""
        self.twin_client.connect()

        fleet = legacy_config.get("fleet_registry", {})
        for barge_id, config in fleet.items():
            config["barge_id"] = barge_id
            entity = create_barge_twin_from_legacy(self.twin_client, config)
            print(f"  Created twin: {barge_id} ({config.get('vessel_name', 'Unknown')})")

    def _setup_simulation(self) -> None:
        """Configure the telemetry simulator."""
        config = SimulationConfig(
            mode=self.mode,
            barge_id="BARGE-DELTA-001",
            vessel_name="Delta Pioneer",
            duration_seconds=self.duration_seconds,
            update_interval_ms=1000,
            noise_factor=0.02,
            target_cargo_tons=1800.0,
            max_draft_m=3.8,
            max_cargo_tons=2200.0,
            light_draft_m=1.8,
        )

        self.simulator = TelemetrySimulator(config)
        self.simulator.set_bridge(self.bridge)

        # Register callbacks
        self.simulator.register_callback("on_state_update", self._on_state_update)
        self.simulator.register_callback("on_complete", self._on_simulation_complete)

        # Register bridge callbacks
        self.bridge.register_callback("on_stability_alert", self._on_stability_alert)

    def _on_state_update(self, state: BargeState) -> None:
        """Handle state update from simulator."""
        self.status.update_vessel(state)

    def _on_stability_alert(
        self,
        barge_id: str,
        prev_status: StabilityStatus,
        new_status: StabilityStatus,
        health_score: float
    ) -> None:
        """Handle stability status change."""
        print(f"\n[ALERT] {barge_id}: {prev_status.value} -> {new_status.value} "
              f"(Health: {health_score:.1f}%)")

    def _on_simulation_complete(self, final_state: BargeState) -> None:
        """Handle simulation completion."""
        print("\n" + "=" * 60)
        print("  SIMULATION COMPLETE")
        print("=" * 60)
        print(f"  Final Cargo: {final_state.cargo_tons:.1f} tons")
        print(f"  Final Draft: {final_state.midship_draft_m:.3f}m")
        print(f"  Health Score: {final_state.health_score:.1f}%")
        print("=" * 60 + "\n")

    def run(self) -> None:
        """Run the simulation."""
        self._running = True
        self._start_time = time.time()

        print("[RUN] Starting Lattice Core simulation...")
        print(f"[RUN] Mode: {self.mode.value}")
        print(f"[RUN] Duration: {self.duration_seconds} seconds ({self.duration_seconds // 60} minutes)")
        print(f"[RUN] Dashboard: http://localhost:{self.dashboard_port}\n")

        # Start simulator
        self.simulator.start()

        # Main status loop
        try:
            while self._running:
                status = self.simulator.get_status()

                if not status["running"]:
                    self._running = False
                    break

                self._print_status(status)
                time.sleep(5)  # Update console every 5 seconds

        except KeyboardInterrupt:
            print("\n[STOP] Simulation interrupted by user.")
            self.simulator.stop()

        self._running = False

    def _print_status(self, status: dict) -> None:
        """Print simulation status to console."""
        state = status.get("current_state", {})

        elapsed = status.get("elapsed_seconds", 0)
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)

        print(f"\r[{mins:02d}:{secs:02d}] "
              f"Draft: {state.get('midship_draft_m', 0):.2f}m | "
              f"Cargo: {state.get('cargo_tons', 0):.0f}t | "
              f"Health: {state.get('health_score', 0):.0f}% | "
              f"Status: {state.get('stability_status', 'N/A')}", end="", flush=True)

    def get_dashboard_payload(self) -> str:
        """Get current status as JSON for dashboard."""
        return self.status.get_dashboard_json()


def run_demo():
    """Run the Lattice Core demo with default settings."""
    parser = argparse.ArgumentParser(description="Lattice Core Simulation Runner")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["LOADING", "TRANSIT", "UNLOADING", "STRESS", "STATIC"],
        default="LOADING",
        help="Simulation mode"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=600,
        help="Simulation duration in seconds (default: 600 = 10 minutes)"
    )
    parser.add_argument(
        "--project",
        type=str,
        default="",
        help="GCP project ID"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Dashboard server port"
    )

    args = parser.parse_args()

    mode = SimulationMode[args.mode]

    runner = LatticeCoreDemoRunner(
        project_id=args.project,
        mode=mode,
        duration_seconds=args.duration,
        dashboard_port=args.port
    )

    runner.setup()
    runner.run()


if __name__ == "__main__":
    run_demo()
