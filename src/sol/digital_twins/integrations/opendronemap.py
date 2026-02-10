"""
OpenDroneMap Integration for FREQ SOL

Integrates OpenDroneMap (NodeODM) photogrammetry processing with
Azure Digital Twins for VECTOR GAMMA maritime barge drafting operations.

Azure Marketplace: OpenDroneMap by bCloud LLC
- VM: Ubuntu 24.04 with ODM 3.5.6
- Cost: $0.038/hour
- API: NodeODM REST API

Workflow:
    Drone SCAN → OpenDroneMap PROCESS → Point Cloud → Digital Twins → TOM REPORT
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import urllib.request
import urllib.parse
import urllib.error


class TaskStatus(Enum):
    """OpenDroneMap task processing status."""
    QUEUED = 10
    RUNNING = 20
    FAILED = 30
    COMPLETED = 40
    CANCELED = 50


class OutputType(Enum):
    """Available output types from OpenDroneMap processing."""
    ORTHOPHOTO = "orthophoto.tif"
    POINT_CLOUD = "georeferenced_model.laz"
    POINT_CLOUD_PLY = "georeferenced_model.ply"
    TEXTURED_MODEL = "textured_model.zip"
    DEM = "dsm.tif"
    DTM = "dtm.tif"
    REPORT = "report.pdf"
    SHOTS = "shots.geojson"
    CAMERAS = "cameras.json"
    ALL = "all.zip"


@dataclass
class ProcessingOptions:
    """
    OpenDroneMap processing options for VECTOR GAMMA maritime scanning.

    Default settings optimized for:
    - High accuracy draft measurements (99.8% target)
    - Water surface detection
    - LiDAR point cloud generation
    """

    # Core processing
    dsm: bool = True                      # Digital Surface Model
    dtm: bool = True                      # Digital Terrain Model
    orthophoto_resolution: float = 1.0    # cm/pixel
    pc_quality: str = "high"              # Point cloud quality: ultra, high, medium, low
    pc_geometric: bool = True             # Improve point cloud geometric accuracy

    # Feature extraction
    feature_quality: str = "high"         # Feature extraction quality
    feature_type: str = "sift"            # Feature type: sift, orb, hahog

    # Mesh generation
    mesh_octree_depth: int = 12           # Octree depth for mesh
    mesh_size: int = 300000               # Max mesh vertices

    # Maritime-specific optimizations
    radiometric_calibration: str = "camera"  # Radiometric calibration
    texturing_skip_global_seam_leveling: bool = True  # Better for water
    use_3dmesh: bool = True               # Generate 3D textured mesh

    # GPS/Georeferencing
    gps_accuracy: float = 2.0             # GPS accuracy in meters
    use_exif: bool = True                 # Use EXIF data for georeferencing

    # Output formats
    pc_las: bool = True                   # Output LAS point cloud
    pc_ept: bool = True                   # Output Entwine Point Tile

    def to_dict(self) -> Dict[str, Any]:
        """Convert options to NodeODM API format."""
        return [
            {"name": "dsm", "value": self.dsm},
            {"name": "dtm", "value": self.dtm},
            {"name": "orthophoto-resolution", "value": self.orthophoto_resolution},
            {"name": "pc-quality", "value": self.pc_quality},
            {"name": "pc-geometric", "value": self.pc_geometric},
            {"name": "feature-quality", "value": self.feature_quality},
            {"name": "feature-type", "value": self.feature_type},
            {"name": "mesh-octree-depth", "value": self.mesh_octree_depth},
            {"name": "mesh-size", "value": self.mesh_size},
            {"name": "radiometric-calibration", "value": self.radiometric_calibration},
            {"name": "texturing-skip-global-seam-leveling", "value": self.texturing_skip_global_seam_leveling},
            {"name": "use-3dmesh", "value": self.use_3dmesh},
            {"name": "gps-accuracy", "value": self.gps_accuracy},
            {"name": "use-exif", "value": self.use_exif},
            {"name": "pc-las", "value": self.pc_las},
            {"name": "pc-ept", "value": self.pc_ept},
        ]


@dataclass
class ODMTask:
    """Represents an OpenDroneMap processing task."""

    uuid: str
    name: str
    status: TaskStatus
    created_at: datetime
    processing_time: int = 0              # seconds
    images_count: int = 0
    progress: float = 0.0                 # 0-100
    options: Optional[ProcessingOptions] = None
    output_path: Optional[str] = None
    error: Optional[str] = None

    # VECTOR GAMMA metadata
    mission_id: Optional[str] = None
    drone_id: Optional[str] = None
    barge_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "status": self.status.name,
            "created_at": self.created_at.isoformat(),
            "processing_time": self.processing_time,
            "images_count": self.images_count,
            "progress": self.progress,
            "output_path": self.output_path,
            "error": self.error,
            "mission_id": self.mission_id,
            "drone_id": self.drone_id,
            "barge_id": self.barge_id,
        }


@dataclass
class ODMProject:
    """Represents an OpenDroneMap project for VECTOR GAMMA mission."""

    project_id: str
    name: str
    description: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    tasks: List[ODMTask] = field(default_factory=list)

    # VECTOR GAMMA mission binding
    mission_id: Optional[str] = None
    vector: str = "GAMMA"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "tasks": [t.to_dict() for t in self.tasks],
            "mission_id": self.mission_id,
            "vector": self.vector,
        }


class OpenDroneMapClient:
    """
    Client for OpenDroneMap (NodeODM) integration.

    Connects to OpenDroneMap VM on Azure for processing drone imagery
    into point clouds and 3D models for Digital Twins synchronization.

    Azure Marketplace Configuration:
        Publisher: bCloud LLC
        Product: OpenDroneMap
        VM Size: Recommend Standard_D4s_v3 or higher for production
        Cost: $0.038/hour base + VM compute

    Usage:
        client = OpenDroneMapClient("http://your-odm-vm:3000")
        task = client.create_task(
            name="barge-scan-001",
            images=["img1.jpg", "img2.jpg", ...],
            options=ProcessingOptions()
        )
        client.wait_for_completion(task.uuid)
        point_cloud = client.download_output(task.uuid, OutputType.POINT_CLOUD)
    """

    DEFAULT_PORT = 3000

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize OpenDroneMap client.

        Args:
            host: NodeODM server hostname or IP
            port: NodeODM API port (default: 3000)
            token: Optional authentication token
            timeout: Request timeout in seconds
        """
        self.host = host.rstrip("/")
        self.port = port
        self.token = token
        self.timeout = timeout

        # Remove protocol if included
        if "://" in self.host:
            self.host = self.host.split("://")[1]

        self._base_url = f"http://{self.host}:{self.port}"
        self._tasks_cache: Dict[str, ODMTask] = {}

    @property
    def base_url(self) -> str:
        """Get the NodeODM API base URL."""
        return self._base_url

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to NodeODM API."""
        url = f"{self._base_url}{endpoint}"

        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            if method == "GET":
                if data:
                    url += "?" + urllib.parse.urlencode(data)
                req = urllib.request.Request(url, headers=headers)
            elif method == "POST":
                if data:
                    post_data = json.dumps(data).encode("utf-8")
                    headers["Content-Type"] = "application/json"
                else:
                    post_data = None
                req = urllib.request.Request(url, data=post_data, headers=headers, method="POST")
            else:
                req = urllib.request.Request(url, headers=headers, method=method)

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))

        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"error": f"Connection failed: {e.reason}"}
        except Exception as e:
            return {"error": str(e)}

    def get_info(self) -> Dict[str, Any]:
        """
        Get NodeODM server information.

        Returns server version, available options, and task queue status.
        """
        return self._request("GET", "/info")

    def get_options(self) -> List[Dict[str, Any]]:
        """Get available processing options."""
        return self._request("GET", "/options")

    def create_task(
        self,
        name: str,
        images: List[str],
        options: Optional[ProcessingOptions] = None,
        mission_id: Optional[str] = None,
        drone_id: Optional[str] = None,
        barge_id: Optional[str] = None,
        webhook: Optional[str] = None
    ) -> ODMTask:
        """
        Create a new processing task.

        Args:
            name: Task name
            images: List of image file paths to process
            options: Processing options (defaults to VECTOR GAMMA optimized)
            mission_id: VECTOR GAMMA mission ID
            drone_id: Source drone twin ID
            barge_id: Target barge twin ID
            webhook: URL to notify on completion

        Returns:
            ODMTask with task UUID and initial status
        """
        if options is None:
            options = ProcessingOptions()

        task_data = {
            "name": name,
            "options": options.to_dict(),
        }

        if webhook:
            task_data["webhook"] = webhook

        # Note: Actual file upload would use multipart form data
        # This is a simplified version - production would use requests library
        result = self._request("POST", "/task/new/init", task_data)

        if "error" in result:
            raise Exception(f"Failed to create task: {result['error']}")

        task = ODMTask(
            uuid=result.get("uuid", ""),
            name=name,
            status=TaskStatus.QUEUED,
            created_at=datetime.utcnow(),
            images_count=len(images),
            options=options,
            mission_id=mission_id,
            drone_id=drone_id,
            barge_id=barge_id,
        )

        self._tasks_cache[task.uuid] = task
        return task

    def get_task_info(self, task_uuid: str) -> ODMTask:
        """
        Get current task information and status.

        Args:
            task_uuid: Task UUID

        Returns:
            Updated ODMTask
        """
        result = self._request("GET", f"/task/{task_uuid}/info")

        if "error" in result:
            raise Exception(f"Failed to get task info: {result['error']}")

        status_code = result.get("status", {}).get("code", 10)
        status = TaskStatus(status_code)

        task = ODMTask(
            uuid=task_uuid,
            name=result.get("name", ""),
            status=status,
            created_at=datetime.fromisoformat(
                result.get("dateCreated", datetime.utcnow().isoformat())
            ),
            processing_time=result.get("processingTime", 0),
            images_count=result.get("imagesCount", 0),
            progress=result.get("progress", 0.0),
        )

        # Preserve VECTOR GAMMA metadata from cache
        if task_uuid in self._tasks_cache:
            cached = self._tasks_cache[task_uuid]
            task.mission_id = cached.mission_id
            task.drone_id = cached.drone_id
            task.barge_id = cached.barge_id
            task.options = cached.options

        self._tasks_cache[task_uuid] = task
        return task

    def wait_for_completion(
        self,
        task_uuid: str,
        poll_interval: int = 10,
        timeout: Optional[int] = None,
        progress_callback: Optional[callable] = None
    ) -> ODMTask:
        """
        Wait for task to complete.

        Args:
            task_uuid: Task UUID
            poll_interval: Seconds between status checks
            timeout: Maximum wait time in seconds (None = unlimited)
            progress_callback: Function called with (task, progress) on updates

        Returns:
            Completed ODMTask

        Raises:
            TimeoutError: If timeout exceeded
            Exception: If task fails
        """
        start_time = time.time()

        while True:
            task = self.get_task_info(task_uuid)

            if progress_callback:
                progress_callback(task, task.progress)

            if task.status == TaskStatus.COMPLETED:
                return task

            if task.status == TaskStatus.FAILED:
                raise Exception(f"Task failed: {task.error}")

            if task.status == TaskStatus.CANCELED:
                raise Exception("Task was canceled")

            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task did not complete within {timeout} seconds")

            time.sleep(poll_interval)

    def get_output_url(self, task_uuid: str, output_type: OutputType) -> str:
        """
        Get download URL for task output.

        Args:
            task_uuid: Task UUID
            output_type: Type of output to download

        Returns:
            Download URL
        """
        return f"{self._base_url}/task/{task_uuid}/download/{output_type.value}"

    def download_output(
        self,
        task_uuid: str,
        output_type: OutputType,
        destination: Union[str, Path]
    ) -> Path:
        """
        Download task output to local file.

        Args:
            task_uuid: Task UUID
            output_type: Type of output to download
            destination: Local file path or directory

        Returns:
            Path to downloaded file
        """
        url = self.get_output_url(task_uuid, output_type)
        dest_path = Path(destination)

        if dest_path.is_dir():
            dest_path = dest_path / output_type.value

        urllib.request.urlretrieve(url, str(dest_path))
        return dest_path

    def cancel_task(self, task_uuid: str) -> bool:
        """Cancel a running task."""
        result = self._request("POST", f"/task/{task_uuid}/cancel")
        return result.get("success", False)

    def remove_task(self, task_uuid: str) -> bool:
        """Remove a task and its outputs."""
        result = self._request("POST", f"/task/{task_uuid}/remove")
        if task_uuid in self._tasks_cache:
            del self._tasks_cache[task_uuid]
        return result.get("success", False)

    def get_all_tasks(self) -> List[ODMTask]:
        """Get all tasks on the server."""
        result = self._request("GET", "/task/list")

        if "error" in result:
            return []

        tasks = []
        for task_data in result:
            task = self.get_task_info(task_data.get("uuid", ""))
            tasks.append(task)

        return tasks

    # --- VECTOR GAMMA Convenience Methods ---

    def process_barge_scan(
        self,
        mission_id: str,
        drone_id: str,
        barge_id: str,
        images: List[str],
        high_accuracy: bool = True
    ) -> ODMTask:
        """
        Process a VECTOR GAMMA barge scanning mission.

        Creates an optimized processing task for maritime draft measurement.

        Args:
            mission_id: VECTOR GAMMA mission ID
            drone_id: LiDAR drone twin ID
            barge_id: Target cargo barge twin ID
            images: Drone imagery files
            high_accuracy: Use ultra-high accuracy settings (slower)

        Returns:
            ODMTask configured for barge scanning
        """
        options = ProcessingOptions(
            pc_quality="ultra" if high_accuracy else "high",
            orthophoto_resolution=0.5 if high_accuracy else 1.0,
            mesh_octree_depth=13 if high_accuracy else 12,
            pc_geometric=True,
            dsm=True,
            dtm=True,
        )

        task_name = f"VECTOR_GAMMA_{mission_id}_{barge_id}"

        return self.create_task(
            name=task_name,
            images=images,
            options=options,
            mission_id=mission_id,
            drone_id=drone_id,
            barge_id=barge_id,
        )

    def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary of the OpenDroneMap client status."""
        server_info = self.get_info()

        return {
            "base_url": self._base_url,
            "server_version": server_info.get("version", "unknown"),
            "task_queue_count": server_info.get("taskQueueCount", 0),
            "max_parallel_tasks": server_info.get("maxParallelTasks", 1),
            "cached_tasks": len(self._tasks_cache),
            "connected": "error" not in server_info,
        }
