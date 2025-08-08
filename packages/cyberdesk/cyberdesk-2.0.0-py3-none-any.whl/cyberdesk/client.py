"""Cyberdesk Python SDK Client."""
from typing import Optional, Dict, Any, Union
from uuid import UUID
from pathlib import Path
import httpx
from dataclasses import dataclass

# Import the generated client
from openapi_client.cyberdesk_cloud_client import AuthenticatedClient
from openapi_client.cyberdesk_cloud_client.types import UNSET, Unset
from openapi_client.cyberdesk_cloud_client.api.machines import (
    list_machines_v1_machines_get,
    create_machine_v1_machines_post,
    get_machine_v1_machines_machine_id_get,
    update_machine_v1_machines_machine_id_patch,
    delete_machine_v1_machines_machine_id_delete,
)
from openapi_client.cyberdesk_cloud_client.api.workflows import (
    list_workflows_v1_workflows_get,
    create_workflow_v1_workflows_post,
    get_workflow_v1_workflows_workflow_id_get,
    update_workflow_v1_workflows_workflow_id_patch,
    delete_workflow_v1_workflows_workflow_id_delete,
)
from openapi_client.cyberdesk_cloud_client.api.runs import (
    list_runs_v1_runs_get,
    create_run_v1_runs_post,
    get_run_v1_runs_run_id_get,
    update_run_v1_runs_run_id_patch,
    delete_run_v1_runs_run_id_delete,
    bulk_create_runs_v1_runs_bulk_post,
)
from openapi_client.cyberdesk_cloud_client.api.connections import (
    list_connections_v1_connections_get,
    create_connection_v1_connections_post,
)
from openapi_client.cyberdesk_cloud_client.api.trajectories import (
    list_trajectories_v1_trajectories_get,
    create_trajectory_v1_trajectories_post,
    get_trajectory_v1_trajectories_trajectory_id_get,
    update_trajectory_v1_trajectories_trajectory_id_patch,
    delete_trajectory_v1_trajectories_trajectory_id_delete,
    get_latest_trajectory_for_workflow_v1_workflows_workflow_id_latest_trajectory_get,
)
from openapi_client.cyberdesk_cloud_client.api.run_attachments import (
    list_run_attachments_v1_run_attachments_get,
    create_run_attachment_v1_run_attachments_post,
    get_run_attachment_v1_run_attachments_attachment_id_get,
    download_run_attachment_v1_run_attachments_attachment_id_download_get,
    get_run_attachment_download_url_v1_run_attachments_attachment_id_download_url_get,
    update_run_attachment_v1_run_attachments_attachment_id_put,
    delete_run_attachment_v1_run_attachments_attachment_id_delete,
)

# Import models
from openapi_client.cyberdesk_cloud_client.models import (
    MachineCreate,
    MachineUpdate,
    MachineResponse,
    MachineStatus,
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    RunCreate,
    RunUpdate,
    RunResponse,
    RunStatus,
    RunBulkCreate,
    RunBulkCreateResponse,
    FileInput,
    ConnectionCreate,
    ConnectionResponse,
    ConnectionStatus,
    TrajectoryCreate,
    TrajectoryUpdate,
    TrajectoryResponse,
    RunAttachmentCreate,
    RunAttachmentUpdate,
    RunAttachmentResponse,
    RunAttachmentDownloadUrlResponse,
    AttachmentType,
    PaginatedResponseMachineResponse,
    PaginatedResponseWorkflowResponse,
    PaginatedResponseRunResponse,
    PaginatedResponseConnectionResponse,
    PaginatedResponseTrajectoryResponse,
    PaginatedResponseRunAttachmentResponse,
)

# Re-export common types
__all__ = [
    "CyberdeskClient",
    "MachineCreate",
    "MachineUpdate",
    "MachineResponse",
    "MachineStatus",
    "WorkflowCreate",
    "WorkflowUpdate",
    "WorkflowResponse",
    "RunCreate",
    "RunUpdate",
    "RunResponse",
    "RunStatus",
    "RunBulkCreate",
    "RunBulkCreateResponse",
    "FileInput",
    "ConnectionCreate",
    "ConnectionResponse",
    "ConnectionStatus",
    "TrajectoryCreate",
    "TrajectoryUpdate",
    "TrajectoryResponse",
    "RunAttachmentCreate",
    "RunAttachmentUpdate",
    "RunAttachmentResponse",
    "RunAttachmentDownloadUrlResponse",
    "AttachmentType",
]

DEFAULT_API_BASE_URL = "https://api.cyberdesk.io"


@dataclass
class ApiResponse:
    """Wrapper for API responses."""
    data: Optional[Any] = None
    error: Optional[Any] = None


def _to_uuid(value: Union[str, UUID]) -> UUID:
    """Convert string to UUID if needed."""
    if isinstance(value, str):
        return UUID(value)
    return value


def _to_unset_or_value(value: Optional[Any]) -> Union[Unset, Any]:
    """Convert None to UNSET."""
    return UNSET if value is None else value


class MachinesAPI:
    """Machines API endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self.client = client
    
    async def list(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[MachineStatus] = None
    ) -> ApiResponse:
        """List machines with optional filtering."""
        try:
            response = await list_machines_v1_machines_get.asyncio(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                status=status
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def list_sync(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[MachineStatus] = None
    ) -> ApiResponse:
        """List machines with optional filtering (synchronous)."""
        try:
            response = list_machines_v1_machines_get.sync(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                status=status
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def create(self, data: MachineCreate) -> ApiResponse:
        """Create a new machine."""
        try:
            response = await create_machine_v1_machines_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def create_sync(self, data: MachineCreate) -> ApiResponse:
        """Create a new machine (synchronous)."""
        try:
            response = create_machine_v1_machines_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get(self, machine_id: str) -> ApiResponse:
        """Get a specific machine by ID."""
        try:
            response = await get_machine_v1_machines_machine_id_get.asyncio(
                client=self.client,
                machine_id=_to_uuid(machine_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_sync(self, machine_id: str) -> ApiResponse:
        """Get a specific machine by ID (synchronous)."""
        try:
            response = get_machine_v1_machines_machine_id_get.sync(
                client=self.client,
                machine_id=_to_uuid(machine_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def update(self, machine_id: str, data: MachineUpdate) -> ApiResponse:
        """Update a machine."""
        try:
            response = await update_machine_v1_machines_machine_id_patch.asyncio(
                client=self.client,
                machine_id=_to_uuid(machine_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def update_sync(self, machine_id: str, data: MachineUpdate) -> ApiResponse:
        """Update a machine (synchronous)."""
        try:
            response = update_machine_v1_machines_machine_id_patch.sync(
                client=self.client,
                machine_id=_to_uuid(machine_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def delete(self, machine_id: str) -> ApiResponse:
        """Delete a machine."""
        try:
            await delete_machine_v1_machines_machine_id_delete.asyncio(
                client=self.client,
                machine_id=_to_uuid(machine_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    def delete_sync(self, machine_id: str) -> ApiResponse:
        """Delete a machine (synchronous)."""
        try:
            delete_machine_v1_machines_machine_id_delete.sync(
                client=self.client,
                machine_id=_to_uuid(machine_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)


class WorkflowsAPI:
    """Workflows API endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self.client = client
    
    async def list(self, skip: Optional[int] = None, limit: Optional[int] = None) -> ApiResponse:
        """List workflows."""
        try:
            response = await list_workflows_v1_workflows_get.asyncio(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def list_sync(self, skip: Optional[int] = None, limit: Optional[int] = None) -> ApiResponse:
        """List workflows (synchronous)."""
        try:
            response = list_workflows_v1_workflows_get.sync(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def create(self, data: WorkflowCreate) -> ApiResponse:
        """Create a new workflow."""
        try:
            response = await create_workflow_v1_workflows_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def create_sync(self, data: WorkflowCreate) -> ApiResponse:
        """Create a new workflow (synchronous)."""
        try:
            response = create_workflow_v1_workflows_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get(self, workflow_id: str) -> ApiResponse:
        """Get a specific workflow by ID."""
        try:
            response = await get_workflow_v1_workflows_workflow_id_get.asyncio(
                client=self.client,
                workflow_id=_to_uuid(workflow_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_sync(self, workflow_id: str) -> ApiResponse:
        """Get a specific workflow by ID (synchronous)."""
        try:
            response = get_workflow_v1_workflows_workflow_id_get.sync(
                client=self.client,
                workflow_id=_to_uuid(workflow_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def update(self, workflow_id: str, data: WorkflowUpdate) -> ApiResponse:
        """Update a workflow."""
        try:
            response = await update_workflow_v1_workflows_workflow_id_patch.asyncio(
                client=self.client,
                workflow_id=_to_uuid(workflow_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def update_sync(self, workflow_id: str, data: WorkflowUpdate) -> ApiResponse:
        """Update a workflow (synchronous)."""
        try:
            response = update_workflow_v1_workflows_workflow_id_patch.sync(
                client=self.client,
                workflow_id=_to_uuid(workflow_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def delete(self, workflow_id: str) -> ApiResponse:
        """Delete a workflow."""
        try:
            await delete_workflow_v1_workflows_workflow_id_delete.asyncio(
                client=self.client,
                workflow_id=_to_uuid(workflow_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    def delete_sync(self, workflow_id: str) -> ApiResponse:
        """Delete a workflow (synchronous)."""
        try:
            delete_workflow_v1_workflows_workflow_id_delete.sync(
                client=self.client,
                workflow_id=_to_uuid(workflow_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)


class RunsAPI:
    """Runs API endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self.client = client
    
    async def list(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[RunStatus] = None,
        workflow_id: Optional[str] = None,
        machine_id: Optional[str] = None
    ) -> ApiResponse:
        """List runs with optional filtering."""
        try:
            response = await list_runs_v1_runs_get.asyncio(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                status=status,
                workflow_id=_to_uuid(workflow_id) if workflow_id else UNSET,
                machine_id=_to_uuid(machine_id) if machine_id else UNSET
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def list_sync(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[RunStatus] = None,
        workflow_id: Optional[str] = None,
        machine_id: Optional[str] = None
    ) -> ApiResponse:
        """List runs with optional filtering (synchronous)."""
        try:
            response = list_runs_v1_runs_get.sync(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                status=status,
                workflow_id=_to_uuid(workflow_id) if workflow_id else UNSET,
                machine_id=_to_uuid(machine_id) if machine_id else UNSET
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def create(self, data: RunCreate) -> ApiResponse:
        """Create a new run."""
        try:
            response = await create_run_v1_runs_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def create_sync(self, data: RunCreate) -> ApiResponse:
        """Create a new run (synchronous)."""
        try:
            response = create_run_v1_runs_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get(self, run_id: str) -> ApiResponse:
        """Get a specific run by ID."""
        try:
            response = await get_run_v1_runs_run_id_get.asyncio(
                client=self.client,
                run_id=_to_uuid(run_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_sync(self, run_id: str) -> ApiResponse:
        """Get a specific run by ID (synchronous)."""
        try:
            response = get_run_v1_runs_run_id_get.sync(
                client=self.client,
                run_id=_to_uuid(run_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def update(self, run_id: str, data: RunUpdate) -> ApiResponse:
        """Update a run."""
        try:
            response = await update_run_v1_runs_run_id_patch.asyncio(
                client=self.client,
                run_id=_to_uuid(run_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def update_sync(self, run_id: str, data: RunUpdate) -> ApiResponse:
        """Update a run (synchronous)."""
        try:
            response = update_run_v1_runs_run_id_patch.sync(
                client=self.client,
                run_id=_to_uuid(run_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def delete(self, run_id: str) -> ApiResponse:
        """Delete a run."""
        try:
            await delete_run_v1_runs_run_id_delete.asyncio(
                client=self.client,
                run_id=_to_uuid(run_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    def delete_sync(self, run_id: str) -> ApiResponse:
        """Delete a run (synchronous)."""
        try:
            delete_run_v1_runs_run_id_delete.sync(
                client=self.client,
                run_id=_to_uuid(run_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    async def bulk_create(self, data: RunBulkCreate) -> ApiResponse:
        """Create multiple runs with the same configuration.
        
        This method efficiently creates multiple runs:
        - All runs are created in a single database transaction
        - Temporal workflows are started asynchronously 
        - Returns immediately with created run details
        
        Args:
            data: RunBulkCreate object containing workflow_id, machine_id, 
                  input_values, file_inputs, and count (max 1000)
        
        Returns:
            ApiResponse with RunBulkCreateResponse containing:
                - created_runs: List of created RunResponse objects
                - failed_count: Number of runs that failed to create
                - errors: List of error messages for failed runs
        """
        try:
            response = await bulk_create_runs_v1_runs_bulk_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def bulk_create_sync(self, data: RunBulkCreate) -> ApiResponse:
        """Create multiple runs with the same configuration (synchronous).
        
        This method efficiently creates multiple runs:
        - All runs are created in a single database transaction
        - Temporal workflows are started asynchronously 
        - Returns immediately with created run details
        
        Args:
            data: RunBulkCreate object containing workflow_id, machine_id, 
                  input_values, file_inputs, and count (max 1000)
        
        Returns:
            ApiResponse with RunBulkCreateResponse containing:
                - created_runs: List of created RunResponse objects
                - failed_count: Number of runs that failed to create
                - errors: List of error messages for failed runs
        """
        try:
            response = bulk_create_runs_v1_runs_bulk_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)


class ConnectionsAPI:
    """Connections API endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self.client = client
    
    async def list(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        machine_id: Optional[str] = None,
        status: Optional[Union[str, ConnectionStatus]] = None
    ) -> ApiResponse:
        """List connections with optional filtering."""
        try:
            # Handle status conversion
            if isinstance(status, str):
                status = Unset if status is None else ConnectionStatus(status)
            
            response = await list_connections_v1_connections_get.asyncio(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                machine_id=_to_uuid(machine_id) if machine_id else UNSET,
                status=status
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def list_sync(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        machine_id: Optional[str] = None,
        status: Optional[Union[str, ConnectionStatus]] = None
    ) -> ApiResponse:
        """List connections with optional filtering (synchronous)."""
        try:
            # Handle status conversion
            if isinstance(status, str):
                status = Unset if status is None else ConnectionStatus(status)
            
            response = list_connections_v1_connections_get.sync(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                machine_id=_to_uuid(machine_id) if machine_id else UNSET,
                status=status
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def create(self, data: ConnectionCreate) -> ApiResponse:
        """Create a new connection."""
        try:
            response = await create_connection_v1_connections_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def create_sync(self, data: ConnectionCreate) -> ApiResponse:
        """Create a new connection (synchronous)."""
        try:
            response = create_connection_v1_connections_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)


class TrajectoriesAPI:
    """Trajectories API endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self.client = client
    
    async def list(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        workflow_id: Optional[str] = None
    ) -> ApiResponse:
        """List trajectories with optional filtering."""
        try:
            response = await list_trajectories_v1_trajectories_get.asyncio(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                workflow_id=_to_uuid(workflow_id) if workflow_id else UNSET
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def list_sync(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        workflow_id: Optional[str] = None
    ) -> ApiResponse:
        """List trajectories with optional filtering (synchronous)."""
        try:
            response = list_trajectories_v1_trajectories_get.sync(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                workflow_id=_to_uuid(workflow_id) if workflow_id else UNSET
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def create(self, data: TrajectoryCreate) -> ApiResponse:
        """Create a new trajectory."""
        try:
            response = await create_trajectory_v1_trajectories_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def create_sync(self, data: TrajectoryCreate) -> ApiResponse:
        """Create a new trajectory (synchronous)."""
        try:
            response = create_trajectory_v1_trajectories_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get(self, trajectory_id: str) -> ApiResponse:
        """Get a specific trajectory by ID."""
        try:
            response = await get_trajectory_v1_trajectories_trajectory_id_get.asyncio(
                client=self.client,
                trajectory_id=_to_uuid(trajectory_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_sync(self, trajectory_id: str) -> ApiResponse:
        """Get a specific trajectory by ID (synchronous)."""
        try:
            response = get_trajectory_v1_trajectories_trajectory_id_get.sync(
                client=self.client,
                trajectory_id=_to_uuid(trajectory_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def update(self, trajectory_id: str, data: TrajectoryUpdate) -> ApiResponse:
        """Update a trajectory."""
        try:
            response = await update_trajectory_v1_trajectories_trajectory_id_patch.asyncio(
                client=self.client,
                trajectory_id=_to_uuid(trajectory_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def update_sync(self, trajectory_id: str, data: TrajectoryUpdate) -> ApiResponse:
        """Update a trajectory (synchronous)."""
        try:
            response = update_trajectory_v1_trajectories_trajectory_id_patch.sync(
                client=self.client,
                trajectory_id=_to_uuid(trajectory_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def delete(self, trajectory_id: str) -> ApiResponse:
        """Delete a trajectory."""
        try:
            await delete_trajectory_v1_trajectories_trajectory_id_delete.asyncio(
                client=self.client,
                trajectory_id=_to_uuid(trajectory_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    def delete_sync(self, trajectory_id: str) -> ApiResponse:
        """Delete a trajectory (synchronous)."""
        try:
            delete_trajectory_v1_trajectories_trajectory_id_delete.sync(
                client=self.client,
                trajectory_id=_to_uuid(trajectory_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get_latest_for_workflow(self, workflow_id: str) -> ApiResponse:
        """Get the latest trajectory for a workflow."""
        try:
            response = await get_latest_trajectory_for_workflow_v1_workflows_workflow_id_latest_trajectory_get.asyncio(
                client=self.client,
                workflow_id=_to_uuid(workflow_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_latest_for_workflow_sync(self, workflow_id: str) -> ApiResponse:
        """Get the latest trajectory for a workflow (synchronous)."""
        try:
            response = get_latest_trajectory_for_workflow_v1_workflows_workflow_id_latest_trajectory_get.sync(
                client=self.client,
                workflow_id=_to_uuid(workflow_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)


class RunAttachmentsAPI:
    """Run Attachments API endpoints."""
    
    def __init__(self, client: AuthenticatedClient):
        self.client = client
    
    async def list(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        run_id: Optional[str] = None,
        attachment_type: Optional[AttachmentType] = None
    ) -> ApiResponse:
        """List run attachments with optional filtering."""
        try:
            response = await list_run_attachments_v1_run_attachments_get.asyncio(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                run_id=_to_uuid(run_id) if run_id else UNSET,
                attachment_type=attachment_type
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def list_sync(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        run_id: Optional[str] = None,
        attachment_type: Optional[AttachmentType] = None
    ) -> ApiResponse:
        """List run attachments with optional filtering (synchronous)."""
        try:
            response = list_run_attachments_v1_run_attachments_get.sync(
                client=self.client,
                skip=_to_unset_or_value(skip),
                limit=_to_unset_or_value(limit),
                run_id=_to_uuid(run_id) if run_id else UNSET,
                attachment_type=attachment_type
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def create(self, data: RunAttachmentCreate) -> ApiResponse:
        """Create a new run attachment."""
        try:
            response = await create_run_attachment_v1_run_attachments_post.asyncio(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def create_sync(self, data: RunAttachmentCreate) -> ApiResponse:
        """Create a new run attachment (synchronous)."""
        try:
            response = create_run_attachment_v1_run_attachments_post.sync(
                client=self.client,
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get(self, attachment_id: str) -> ApiResponse:
        """Get a specific run attachment by ID."""
        try:
            response = await get_run_attachment_v1_run_attachments_attachment_id_get.asyncio(
                client=self.client,
                attachment_id=_to_uuid(attachment_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_sync(self, attachment_id: str) -> ApiResponse:
        """Get a specific run attachment by ID (synchronous)."""
        try:
            response = get_run_attachment_v1_run_attachments_attachment_id_get.sync(
                client=self.client,
                attachment_id=_to_uuid(attachment_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def get_download_url(
        self, 
        attachment_id: str,
        expires_in: Optional[int] = None
    ) -> ApiResponse:
        """Get a signed download URL for a run attachment.
        
        The returned URL will trigger an automatic download when accessed in a browser.
        
        Args:
            attachment_id: The ID of the attachment
            expires_in: URL expiration time in seconds (10-3600). Default: 300 (5 minutes)
        
        Returns:
            ApiResponse with RunAttachmentDownloadUrlResponse containing:
                - url: The signed download URL
                - expires_in: The expiration time in seconds
        """
        try:
            response = await get_run_attachment_download_url_v1_run_attachments_attachment_id_download_url_get.asyncio(
                client=self.client,
                attachment_id=_to_uuid(attachment_id),
                expires_in=_to_unset_or_value(expires_in)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def get_download_url_sync(
        self, 
        attachment_id: str,
        expires_in: Optional[int] = None
    ) -> ApiResponse:
        """Get a signed download URL for a run attachment (synchronous).
        
        The returned URL will trigger an automatic download when accessed in a browser.
        
        Args:
            attachment_id: The ID of the attachment
            expires_in: URL expiration time in seconds (10-3600). Default: 300 (5 minutes)
        
        Returns:
            ApiResponse with RunAttachmentDownloadUrlResponse containing:
                - url: The signed download URL
                - expires_in: The expiration time in seconds
        """
        try:
            response = get_run_attachment_download_url_v1_run_attachments_attachment_id_download_url_get.sync(
                client=self.client,
                attachment_id=_to_uuid(attachment_id),
                expires_in=_to_unset_or_value(expires_in)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def download(self, attachment_id: str) -> ApiResponse:
        """Download a run attachment file directly.
        
        This method returns the raw file content as bytes. For a download URL instead,
        use get_download_url().
        
        Args:
            attachment_id: The ID of the attachment to download
        
        Returns:
            ApiResponse with data containing the raw file bytes
        """
        try:
            response = await download_run_attachment_v1_run_attachments_attachment_id_download_get.asyncio(
                client=self.client,
                attachment_id=_to_uuid(attachment_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def download_sync(self, attachment_id: str) -> ApiResponse:
        """Download a run attachment file directly (synchronous).
        
        This method returns the raw file content as bytes. For a download URL instead,
        use get_download_url_sync().
        
        Args:
            attachment_id: The ID of the attachment to download
        
        Returns:
            ApiResponse with data containing the raw file bytes
        """
        try:
            response = download_run_attachment_v1_run_attachments_attachment_id_download_get.sync(
                client=self.client,
                attachment_id=_to_uuid(attachment_id)
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def update(self, attachment_id: str, data: RunAttachmentUpdate) -> ApiResponse:
        """Update a run attachment (e.g., set expiration)."""
        try:
            response = await update_run_attachment_v1_run_attachments_attachment_id_put.asyncio(
                client=self.client,
                attachment_id=_to_uuid(attachment_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    def update_sync(self, attachment_id: str, data: RunAttachmentUpdate) -> ApiResponse:
        """Update a run attachment (e.g., set expiration) (synchronous)."""
        try:
            response = update_run_attachment_v1_run_attachments_attachment_id_put.sync(
                client=self.client,
                attachment_id=_to_uuid(attachment_id),
                body=data
            )
            return ApiResponse(data=response)
        except Exception as e:
            return ApiResponse(error=e)
    
    async def delete(self, attachment_id: str) -> ApiResponse:
        """Delete a run attachment."""
        try:
            await delete_run_attachment_v1_run_attachments_attachment_id_delete.asyncio(
                client=self.client,
                attachment_id=_to_uuid(attachment_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    def delete_sync(self, attachment_id: str) -> ApiResponse:
        """Delete a run attachment (synchronous)."""
        try:
            delete_run_attachment_v1_run_attachments_attachment_id_delete.sync(
                client=self.client,
                attachment_id=_to_uuid(attachment_id)
            )
            return ApiResponse(data={"success": True})
        except Exception as e:
            return ApiResponse(error=e)
    
    async def save_to_file(
        self,
        attachment_id: str,
        output_path: Optional[Union[str, Path]] = None,
        use_original_filename: bool = True
    ) -> ApiResponse:
        """Download and save a run attachment to a file.
        
        This is a convenience method that combines getting attachment info
        and downloading the file content.
        
        Args:
            attachment_id: The ID of the attachment to download
            output_path: Path where to save the file. If None and use_original_filename
                        is True, saves to current directory with original filename.
            use_original_filename: If True and output_path is a directory, uses the
                                 attachment's original filename.
        
        Returns:
            ApiResponse with data containing the saved file path
        """
        try:
            # Get attachment info for filename
            info_response = await self.get(attachment_id)
            if info_response.error:
                return info_response
            
            attachment_info = info_response.data
            
            # Download the file content
            download_response = await self.download(attachment_id)
            if download_response.error:
                return download_response
            
            # Determine output path
            if output_path is None:
                output_path = Path(attachment_info.filename)
            else:
                output_path = Path(output_path)
                if output_path.is_dir() and use_original_filename:
                    output_path = output_path / attachment_info.filename
            
            # Save to file
            output_path.write_bytes(download_response.data)
            
            return ApiResponse(data={"path": str(output_path), "size": len(download_response.data)})
        except Exception as e:
            return ApiResponse(error=e)
    
    def save_to_file_sync(
        self,
        attachment_id: str,
        output_path: Optional[Union[str, Path]] = None,
        use_original_filename: bool = True
    ) -> ApiResponse:
        """Download and save a run attachment to a file (synchronous).
        
        This is a convenience method that combines getting attachment info
        and downloading the file content.
        
        Args:
            attachment_id: The ID of the attachment to download
            output_path: Path where to save the file. If None and use_original_filename
                        is True, saves to current directory with original filename.
            use_original_filename: If True and output_path is a directory, uses the
                                 attachment's original filename.
        
        Returns:
            ApiResponse with data containing the saved file path
        """
        try:
            # Get attachment info for filename
            info_response = self.get_sync(attachment_id)
            if info_response.error:
                return info_response
            
            attachment_info = info_response.data
            
            # Download the file content
            download_response = self.download_sync(attachment_id)
            if download_response.error:
                return download_response
            
            # Determine output path
            if output_path is None:
                output_path = Path(attachment_info.filename)
            else:
                output_path = Path(output_path)
                if output_path.is_dir() and use_original_filename:
                    output_path = output_path / attachment_info.filename
            
            # Save to file
            output_path.write_bytes(download_response.data)
            
            return ApiResponse(data={"path": str(output_path), "size": len(download_response.data)})
        except Exception as e:
            return ApiResponse(error=e)


class CyberdeskClient:
    """Main Cyberdesk SDK client."""
    
    def __init__(self, api_key: str, base_url: str = DEFAULT_API_BASE_URL):
        """Initialize the Cyberdesk client.
        
        Args:
            api_key: Your Cyberdesk API key
            base_url: API base URL (defaults to https://api.cyberdesk.io)
        """
        # Create the underlying client with authentication
        self._client = AuthenticatedClient(
            base_url=base_url,
            token=api_key,
            prefix="Bearer",
            auth_header_name="Authorization"
        )
        
        # Initialize API endpoints
        self.machines = MachinesAPI(self._client)
        self.workflows = WorkflowsAPI(self._client)
        self.runs = RunsAPI(self._client)
        self.connections = ConnectionsAPI(self._client)
        self.trajectories = TrajectoriesAPI(self._client)
        self.run_attachments = RunAttachmentsAPI(self._client)
        
        # TODO: Add computer API for screenshot functionality
        # The openapi-python-client doesn't generate code for binary responses like PNG images
        # To add screenshot support, implement a ComputerAPI class that:
        # - Makes raw HTTP GET request to /v1/computer/{machine_id}/display/screenshot
        # - Returns the PNG image bytes
        # Example: self.computer = ComputerAPI(self._client)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def close(self):
        """Close the client connection."""
        if hasattr(self._client, '__exit__'):
            self._client.__exit__(None, None, None) 