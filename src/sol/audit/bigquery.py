"""
BigQuery Audit Trail

All SOL operations require a BigQuery audit trail for
FREQ LAW compliance. This module provides the interface
for logging operations to BigQuery.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import json


@dataclass
class AuditEntry:
    """Represents a single audit log entry."""
    
    id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    operation: str = ""
    node_id: str = ""
    node_type: str = ""
    request_payload: Dict[str, Any] = field(default_factory=dict)
    response_payload: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    quorum_required: bool = False
    quorum_achieved: bool = False
    veto_applied: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_bigquery_row(self) -> Dict[str, Any]:
        """Convert to BigQuery row format."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "operation": self.operation,
            "node_id": self.node_id,
            "node_type": self.node_type,
            "request_payload": json.dumps(self.request_payload),
            "response_payload": json.dumps(self.response_payload),
            "execution_time_ms": self.execution_time_ms,
            "success": self.success,
            "error_message": self.error_message,
            "quorum_required": self.quorum_required,
            "quorum_achieved": self.quorum_achieved,
            "veto_applied": self.veto_applied,
            "metadata": json.dumps(self.metadata)
        }


class BigQueryAuditTrail:
    """
    BigQuery Audit Trail Manager
    
    Manages audit logging to BigQuery for FREQ LAW compliance.
    All lattice operations are logged with full context for
    traceability and compliance reporting.
    """
    
    # BigQuery schema for audit table
    SCHEMA = [
        {"name": "id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "operation", "type": "STRING", "mode": "REQUIRED"},
        {"name": "node_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "node_type", "type": "STRING", "mode": "REQUIRED"},
        {"name": "request_payload", "type": "STRING", "mode": "NULLABLE"},
        {"name": "response_payload", "type": "STRING", "mode": "NULLABLE"},
        {"name": "execution_time_ms", "type": "FLOAT", "mode": "REQUIRED"},
        {"name": "success", "type": "BOOLEAN", "mode": "REQUIRED"},
        {"name": "error_message", "type": "STRING", "mode": "NULLABLE"},
        {"name": "quorum_required", "type": "BOOLEAN", "mode": "REQUIRED"},
        {"name": "quorum_achieved", "type": "BOOLEAN", "mode": "REQUIRED"},
        {"name": "veto_applied", "type": "BOOLEAN", "mode": "REQUIRED"},
        {"name": "metadata", "type": "STRING", "mode": "NULLABLE"}
    ]
    
    def __init__(self, project_id: str = "", dataset_id: str = "sol_audit",
                 table_id: str = "operations"):
        """
        Initialize BigQuery Audit Trail.
        
        Args:
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self._buffer: List[AuditEntry] = []
        self._buffer_size = 100
        self._client = None  # Will be initialized on first use
    
    @property
    def full_table_id(self) -> str:
        """Get fully qualified table ID."""
        return f"{self.project_id}.{self.dataset_id}.{self.table_id}"
    
    def log(self, entry: AuditEntry) -> None:
        """
        Add an audit entry to the buffer.
        
        Args:
            entry: AuditEntry to log
        """
        if not entry.id:
            import uuid
            entry.id = str(uuid.uuid4())
        
        self._buffer.append(entry)
        
        # Auto-flush if buffer is full
        if len(self._buffer) >= self._buffer_size:
            self.flush()
    
    def log_operation(
        self,
        operation: str,
        node_id: str,
        node_type: str,
        request_payload: Dict[str, Any],
        response_payload: Dict[str, Any],
        execution_time_ms: float,
        success: bool = True,
        error_message: Optional[str] = None,
        quorum_required: bool = False,
        quorum_achieved: bool = False,
        veto_applied: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log an operation with full context.
        
        Returns:
            Audit entry ID
        """
        import uuid
        entry_id = str(uuid.uuid4())
        
        entry = AuditEntry(
            id=entry_id,
            operation=operation,
            node_id=node_id,
            node_type=node_type,
            request_payload=request_payload,
            response_payload=response_payload,
            execution_time_ms=execution_time_ms,
            success=success,
            error_message=error_message,
            quorum_required=quorum_required,
            quorum_achieved=quorum_achieved,
            veto_applied=veto_applied,
            metadata=metadata or {}
        )
        
        self.log(entry)
        return entry_id
    
    def flush(self) -> int:
        """
        Flush buffered entries to BigQuery.
        
        Returns:
            Number of entries flushed
        """
        if not self._buffer:
            return 0
        
        count = len(self._buffer)
        rows = [entry.to_bigquery_row() for entry in self._buffer]
        
        # In production, this would write to BigQuery
        # For now, we just clear the buffer
        # self._write_to_bigquery(rows)
        
        self._buffer = []
        return count
    
    def get_pending_entries(self) -> List[Dict[str, Any]]:
        """Get entries pending flush."""
        return [entry.to_bigquery_row() for entry in self._buffer]
    
    def get_buffer_size(self) -> int:
        """Get current buffer size."""
        return len(self._buffer)
    
    def set_buffer_size(self, size: int) -> None:
        """Set the auto-flush buffer size."""
        self._buffer_size = size
    
    def get_schema(self) -> List[Dict[str, str]]:
        """Get the BigQuery table schema."""
        return self.SCHEMA
    
    def create_table_ddl(self) -> str:
        """
        Generate BigQuery DDL for creating the audit table.
        
        Returns:
            SQL DDL statement
        """
        columns = []
        for col in self.SCHEMA:
            col_def = f"  {col['name']} {col['type']}"
            if col['mode'] == 'REQUIRED':
                col_def += " NOT NULL"
            columns.append(col_def)
        
        ddl = f"""CREATE TABLE IF NOT EXISTS `{self.full_table_id}` (
{chr(10).join(columns)},
  PRIMARY KEY (id) NOT ENFORCED
)
PARTITION BY DATE(timestamp)
CLUSTER BY node_type, operation
OPTIONS(
  description='SOL Audit Trail for FREQ LAW compliance',
  labels=[('environment', 'production'), ('system', 'sol')]
);"""
        
        return ddl
    
    def query_by_node(self, node_id: str, limit: int = 100) -> str:
        """
        Generate query for entries by node.
        
        Returns:
            SQL query string
        """
        return f"""
SELECT *
FROM `{self.full_table_id}`
WHERE node_id = '{node_id}'
ORDER BY timestamp DESC
LIMIT {limit}
"""
    
    def query_by_operation(self, operation: str, limit: int = 100) -> str:
        """
        Generate query for entries by operation.
        
        Returns:
            SQL query string
        """
        return f"""
SELECT *
FROM `{self.full_table_id}`
WHERE operation = '{operation}'
ORDER BY timestamp DESC
LIMIT {limit}
"""
    
    def query_failures(self, hours: int = 24, limit: int = 100) -> str:
        """
        Generate query for failed operations.
        
        Returns:
            SQL query string
        """
        return f"""
SELECT *
FROM `{self.full_table_id}`
WHERE success = FALSE
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {hours} HOUR)
ORDER BY timestamp DESC
LIMIT {limit}
"""
    
    def query_vetoed_operations(self, limit: int = 100) -> str:
        """
        Generate query for vetoed operations.
        
        Returns:
            SQL query string
        """
        return f"""
SELECT *
FROM `{self.full_table_id}`
WHERE veto_applied = TRUE
ORDER BY timestamp DESC
LIMIT {limit}
"""
