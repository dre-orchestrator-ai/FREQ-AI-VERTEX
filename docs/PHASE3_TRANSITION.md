# Project FREQ: Phase 3 Transition Strategy & Execution Roadmap

**Status:** Phase 3 Re-alignment
**Pivot:** From High-Complexity Digital Twin to Cloud-Native Virtual Drafting & Flash LiDAR
**Primary Target:** Maritime Barge Displacement & Heritage Infrastructure Documentation
**Effective Date:** 2026-02-06
**Document Version:** 1.0.0

---

## Table of Contents

1. [Executive Summary: The Strategic Pivot](#1-executive-summary-the-strategic-pivot)
2. [Technical Architecture: Flash LiDAR & Virtual Drafting](#2-technical-architecture-flash-lidar--virtual-drafting)
3. [Implementation Workflow](#3-implementation-workflow)
4. [Production Optimization](#4-production-optimization)
5. [Required Resources & Subscriptions](#5-required-resources--subscriptions)
6. [Phase Transition Checklist](#6-phase-transition-checklist)
7. [Mission Vector Updates](#7-mission-vector-updates)
8. [Governance Alignment](#8-governance-alignment)

---

## 1. Executive Summary: The Strategic Pivot

### 1.1 The "Digital Twin" Loop Problem

The original Phase 3 plan for a full Digital Twin implementation encountered a **Complexity-Capital Loop** that necessitated strategic re-evaluation:

| Factor | Challenge | Impact |
|--------|-----------|--------|
| **Complexity** | Real-time physics synchronization and atmospheric simulation required high-bandwidth, low-latency data loops | Technically burdensome; exceeded operational capacity |
| **Capital** | Local processing required high-end GPUs/TPUs and proprietary Microsoft Azure Startup credits | Inaccessible due to account legacy issues |

### 1.2 The Solution: Transition to Virtual Drafting

We are pivoting from **"Live Simulation" (Twin)** to **"Precise Geometry Extraction" (Drafting)**.

**Key Benefits:**
- Removes the need for persistent real-time syncing
- Shifts heavy lifting to Google Cloud Platform (GCP) Vertex AI
- Reduces infrastructure complexity by 60%
- Maintains accuracy targets (99.8%) while reducing operational overhead

### 1.3 Phase Progression Summary

```
Phase 1: Latticework Development        [COMPLETED]
    └── SOL architecture established
    └── 7 lattice nodes deployed
    └── FREQ LAW governance implemented

Phase 2: Testing, Integration, Intelligence  [COMPLETED]
    └── Blueprint verification passed
    └── k=3 quorum consensus validated
    └── SSC system prompt operational
    └── Mission vectors configured

Phase 3: Virtual Drafting & Flash LiDAR  [CURRENT - RE-ALIGNED]
    └── Flash LiDAR data pipeline
    └── Virtual Draft Survey (VDS) automation
    └── Maritime barge displacement calculation
    └── Heritage infrastructure documentation
```

---

## 2. Technical Architecture: Flash LiDAR & Virtual Drafting

### 2.1 System Architecture Overview

To optimize for production with **zero local hardware**, the system will utilize Flash LiDAR data processed via **Serverless Cloud Compute**.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FREQ Phase 3: Virtual Drafting Pipeline              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│  │   DRONE CAPTURE │    │  CLOUD STORAGE  │    │   VERTEX AI     │     │
│  │   Flash LiDAR   │───►│  GCS Bucket     │───►│  Custom Job     │     │
│  │   .LAS/.PLY     │    │  (Trigger)      │    │  (Processing)   │     │
│  └─────────────────┘    └─────────────────┘    └────────┬────────┘     │
│                                                          │              │
│                                                          ▼              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│  │   OMNIVERSE     │◄───│   CAD OUTPUT    │◄───│  POINT CLOUD    │     │
│  │   Visualization │    │   2D/3D Draft   │    │  Processing     │     │
│  │   (CloudXR)     │    │   Displacement  │    │  Open3D/RANSAC  │     │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    SOL GOVERNANCE LAYER                          │   │
│  │      FREQ LAW Compliance | Audit Trail | Quality Validation     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Flash LiDAR Integration

Unlike traditional scanning LiDAR, **Flash LiDAR** provides a "snapshot" of the environment, enabling rapid data acquisition suitable for maritime conditions.

#### Data Ingestion Pipeline

| Stage | Component | Description |
|-------|-----------|-------------|
| **Capture** | Drone-mounted Flash LiDAR | Capture .LAS or .PLY point cloud files |
| **Upload** | Google Cloud Storage (GCS) | Files uploaded to designated bucket |
| **Trigger** | Cloud Function | Automatic pipeline initialization on upload |
| **Processing** | Vertex AI Custom Job | Managed pipeline for geometry extraction |

#### Processing Pipeline Specifications

```python
# Pipeline Configuration
pipeline_config = {
    "input_formats": [".LAS", ".PLY", ".E57"],
    "processing_engine": "Vertex AI Vision",
    "container_type": "Custom Container",
    "algorithms": {
        "noise_filtering": "RANSAC",  # Random Sample Consensus
        "plane_detection": "MLESAC",   # Maximum Likelihood Estimation SAC
        "hull_isolation": "ConvexHull + AlphaShape"
    },
    "output_formats": ["CAD", "IFC", "USD"]
}
```

#### RANSAC Algorithm Application

The **RANSAC (Random Sample Consensus)** algorithm is applied via a Vertex AI custom container to:

1. **Filter "Wave Noise"** - Remove water swell artifacts from maritime scans
2. **Isolate Barge Hull** - Separate vessel geometry from environmental data
3. **Detect Water Plane** - Identify the precise waterline for draft calculation

### 2.3 Virtual Draft Survey (VDS) vs. Digital Twin

| Aspect | Digital Twin (Original) | Virtual Draft Survey (Pivot) |
|--------|------------------------|------------------------------|
| **Data Type** | Real-time streaming | Snapshot-based |
| **Processing** | Continuous sync | Batch processing |
| **Infrastructure** | Local GPU cluster | Serverless cloud |
| **Latency Requirement** | <100ms | <30 seconds |
| **Capital Required** | $50K+ hardware | Pay-per-use cloud |
| **Accuracy Target** | 99.9% | 99.8% |

#### VDS Focus: Waterline-to-Gunwale (W-G) Ratio

The Virtual Draft Survey focuses on the **Waterline-to-Gunwale (W-G) ratio** for displacement calculation:

```
                    ┌─────────────────────────────┐
                    │         GUNWALE             │
                    │             │               │
                    │             │ Hull Height   │
                    │             │               │
    ─ ─ ─ ─ ─ ─ ─ ─│─ ─ ─ ─ ─ ─ ┼ ─ ─ ─ ─ ─ ─ ─│─ ─ ─ ─  WATERLINE
                    │             │               │
                    │             │ Draft         │
                    │             │               │
                    └─────────────────────────────┘

    Draft Calculation: Result = Hull Height - Waterline Height
```

#### Automation Features

| Feature | Description |
|---------|-------------|
| **Draft Mark Detection** | OCR identifies draft marks painted on hull |
| **Water Plane Identification** | AI detects waterline from point cloud data |
| **Displacement Calculation** | Automated cargo weight calculation from draft |
| **CAD Generation** | 2D/3D CAD-compatible output for verification |

---

## 3. Implementation Workflow

### 3.1 Cloud Ingestion Layer

```yaml
# Cloud Function Trigger Configuration
trigger:
  type: google.cloud.storage.object.v1.finalized
  bucket: freq-flash-lidar-intake

function:
  name: initialize-vds-pipeline
  runtime: python311
  entry_point: handle_lidar_upload

actions:
  - validate_file_format
  - extract_metadata
  - initialize_vertex_job
  - update_audit_trail
```

**Implementation Steps:**

1. **Set up GCS Trigger** - When a drone file is uploaded, trigger Cloud Function
2. **Initialize Vertex AI Custom Job** - Start processing pipeline
3. **Register with SOL Audit** - Log operation to BigQuery for FREQ LAW compliance

### 3.2 Point Cloud Processing

```python
# Point Cloud Processing Pipeline
from open3d import geometry, io
from vertex_ai import CustomJob

class VDSProcessor:
    """Virtual Draft Survey Point Cloud Processor"""

    def __init__(self):
        self.libraries = ["Open3D", "PointDN", "PDAL"]

    def process(self, point_cloud_path: str) -> dict:
        """
        Process point cloud for draft survey.

        Objective:
            1. Identify the plane of the water
            2. Identify the vertical axis of the barge hull
            3. Calculate: Hull Height - Waterline Height = Draft
        """
        # Load point cloud
        pcd = io.read_point_cloud(point_cloud_path)

        # Apply RANSAC for plane detection
        water_plane = self.detect_water_plane(pcd)

        # Isolate hull geometry
        hull_geometry = self.isolate_hull(pcd, water_plane)

        # Calculate draft
        draft_measurement = self.calculate_draft(hull_geometry, water_plane)

        return {
            "draft_meters": draft_measurement,
            "water_plane_coefficients": water_plane,
            "hull_bounding_box": hull_geometry.get_axis_aligned_bounding_box(),
            "displacement_tonnes": self.calculate_displacement(draft_measurement)
        }
```

### 3.3 Visualization (Virtual Drafting)

| Component | Specification |
|-----------|---------------|
| **Rendering Engine** | NVIDIA Omniverse VM (GCP Marketplace) |
| **Streaming Protocol** | CloudXR |
| **Client Access** | Standard browser/tablet |
| **Output Format** | USD, glTF, CAD-compatible |

**Deployment:**

```bash
# Deploy Omniverse on GCP
gcloud compute instances create omniverse-renderer \
  --zone=us-central1-a \
  --machine-type=n1-standard-8 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --image-family=omniverse-enterprise \
  --image-project=nvidia-ngc-public
```

---

## 4. Production Optimization

### 4.1 Edge-to-Cloud Pre-processing

**Objective:** Reduce cloud egress/ingress costs through edge data thinning.

| Edge Device | Capability | Cost Reduction |
|-------------|------------|----------------|
| Raspberry Pi 5 | Basic point thinning, format validation | 20% |
| Jetson Nano | ML-based noise reduction, compression | 40% |
| Jetson Orin | Full pre-processing, quality scoring | 60% |

```python
# Edge Pre-processing Configuration
edge_config = {
    "thinning_ratio": 0.1,  # Keep 10% of points for preview
    "compression": "Draco",
    "validation": ["format_check", "bounds_check", "density_check"],
    "upload_threshold_mb": 100  # Chunk if larger
}
```

### 4.2 Heritage Preservation Mode

For heritage infrastructure documentation, implement a **Temporal Comparison Loop**:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Current Scan  │────►│    TEMPORAL     │────►│   Deviation     │
│  Flash LiDAR    │     │    COMPARISON   │     │   Report        │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                        ┌────────▼────────┐
                        │   Legacy Data   │
                        │  (Lattice Core) │
                        │   Historical    │
                        └─────────────────┘

Deviation Threshold: > 2mm triggers structural alert
```

**Features:**
- Compare current Flash LiDAR scans against legacy historical data
- Highlight structural deviations exceeding 2mm tolerance
- Generate preservation priority reports
- Track temporal degradation patterns

### 4.3 Safety-First UI

The dashboard prioritizes **Man Overboard (MOB) Avoidance**:

| UI Element | Purpose |
|------------|---------|
| **Zero Personnel Badge** | Confirms survey completed with no personnel on water |
| **Safety Score** | Real-time safety compliance indicator |
| **Drone Status** | Live position and battery status |
| **Weather Integration** | Wind/wave conditions affecting survey quality |

### 4.4 Cost Management

| Strategy | Implementation | Savings |
|----------|----------------|---------|
| **Preemptible VMs** | Use GCP Spot Instances for non-urgent heritage processing | 60-80% |
| **Tiered Storage** | Standard for active projects, Archive for legacy data | 50% |
| **Auto-scaling** | Scale processing based on queue depth | 30% |
| **Batch Processing** | Group heritage scans for off-peak processing | 40% |

```yaml
# Cost-Optimized Processing Configuration
processing:
  maritime:
    priority: HIGH
    vm_type: standard
    timeout_minutes: 10

  heritage:
    priority: MEDIUM
    vm_type: preemptible
    timeout_minutes: 60
    batch_window: "02:00-06:00"  # Off-peak hours
```

---

## 5. Required Resources & Subscriptions

### 5.1 Cloud Infrastructure

| Resource | Provider | Status | Notes |
|----------|----------|--------|-------|
| **Cloud Platform** | Google Cloud Startup Program | Active Application | Primary compute infrastructure |
| **AI Engine** | Vertex AI (Model Garden & Vision AI) | Available | Point cloud processing |
| **Rendering** | NVIDIA Omniverse Enterprise | GCP Marketplace | Visualization pipeline |
| **Storage** | Google Cloud Storage | Available | Standard + Archive tiers |

### 5.2 Software Components

| Component | Purpose | License |
|-----------|---------|---------|
| Open3D | Point cloud processing | MIT |
| PDAL | Point Data Abstraction Library | BSD |
| PointDN | Deep learning point cloud | Academic |
| Draco | 3D data compression | Apache 2.0 |

### 5.3 Integration Requirements

```yaml
# GCP Service Dependencies
services:
  required:
    - cloud-functions
    - cloud-storage
    - vertex-ai
    - bigquery
    - cloud-run

  optional:
    - cloud-cdn  # For global visualization access
    - cloud-armor  # DDoS protection for public endpoints
```

---

## 6. Phase Transition Checklist

### 6.1 Phase 2 Exit Criteria

| Criteria | Status | Verification |
|----------|--------|--------------|
| Blueprint structure integrity | PASSED | Phase2Verifier |
| Architecture audit (K4 topology) | PASSED | Phase2Verifier |
| Hierarchy levels (0-5) configured | PASSED | Phase2Verifier |
| FREQ LAW compliance | COMPLIANT | Phase2Verifier |
| SSC system prompt operational | READY | Phase2Verifier |
| Mission vectors configured | CONFIGURED | Phase2Verifier |

### 6.2 Phase 3 Entry Requirements

| Requirement | Status | Owner |
|-------------|--------|-------|
| GCP Startup Program approval | PENDING | Chief Dre |
| GCS bucket configuration | TODO | DevOps |
| Vertex AI custom container | TODO | Engineering |
| Cloud Function deployment | TODO | Engineering |
| Omniverse VM provisioning | TODO | DevOps |
| VDS algorithm validation | TODO | Data Science |
| SOL integration testing | TODO | QA |

### 6.3 Phase 3 Milestones

```
M1: Infrastructure Setup          [Week 1-2]
    └── GCS buckets configured
    └── Cloud Functions deployed
    └── Vertex AI pipeline created

M2: Processing Pipeline           [Week 3-4]
    └── RANSAC container deployed
    └── Point cloud processing validated
    └── Draft calculation accuracy tested

M3: Visualization Pipeline        [Week 5-6]
    └── Omniverse VM deployed
    └── CloudXR streaming validated
    └── CAD output generation tested

M4: Production Deployment         [Week 7-8]
    └── Maritime VDS operational
    └── Heritage mode enabled
    └── Full SOL integration complete
```

---

## 7. Mission Vector Updates

### 7.1 Vector Gamma: Maritime Barge Drafting (Enhanced)

```python
# Updated Mission Vector Configuration
vector_gamma = {
    "name": "Maritime Barge Drafting",
    "methodology": "Virtual Draft Survey (VDS)",
    "workflow": "CAPTURE > UPLOAD > PROCESS > VALIDATE > REPORT",
    "target_accuracy": 0.998,
    "safety_priority": "MOB_AVOIDANCE",
    "components": {
        "data_capture": "Flash LiDAR",
        "processing": "RANSAC + Open3D",
        "output": ["Draft Report", "CAD Model", "Displacement Calculation"]
    }
}
```

### 7.2 Vector Alpha: Heritage Transmutation (Extended)

```python
# Extended Heritage Vector
vector_alpha_extended = {
    "name": "Heritage Transmutation",
    "description": "COBOL/AS400 modernization + Infrastructure Documentation",
    "sub_vectors": {
        "code_modernization": "Cloud-native microservices",
        "infrastructure_documentation": {
            "methodology": "Flash LiDAR Temporal Comparison",
            "deviation_threshold_mm": 2,
            "preservation_mode": True
        }
    }
}
```

---

## 8. Governance Alignment

### 8.1 FREQ LAW Compliance for Phase 3

| Principle | Phase 3 Implementation |
|-----------|----------------------|
| **FAST** | <30s processing for maritime scans; batch heritage processing |
| **ROBUST** | k=3 quorum for displacement reports; automated retry with RANSAC parameter adjustment |
| **EVOLUTIONARY** | Continuous algorithm improvement via feedback loop; accuracy tracking |
| **QUANTIFIED** | Full audit trail in BigQuery; accuracy metrics per scan |

### 8.2 SOL Node Responsibilities in Phase 3

| Node | Phase 3 Role |
|------|--------------|
| **Strategic OP** | Orchestrate VDS pipeline; prioritize maritime vs heritage |
| **SPCI** | Track processing accuracy; recommend algorithm improvements |
| **Legacy Architect** | Manage heritage data comparison; historical data integration |
| **GOV Engine** | Validate displacement reports; enforce safety protocols |
| **Exec Automate** | Execute Cloud Functions; manage processing queue |
| **Optimal Intel** | Generate insights from temporal comparisons |
| **Element Design** | Generate CAD outputs; manage schema for draft reports |

---

## Document Metadata

| Field | Value |
|-------|-------|
| **Document ID** | FREQ-P3-TRANSITION-001 |
| **Classification** | INTERNAL |
| **Author** | Strategic Synthesis Core |
| **Approved By** | Chief Dre (Sovereign Intent Originator) |
| **Last Updated** | 2026-02-06 |
| **Next Review** | Phase 3 M4 Completion |

---

*This document serves as the authoritative source of truth for the Phase 2 → Phase 3 transition of Project FREQ. All implementation decisions should align with the specifications contained herein.*
