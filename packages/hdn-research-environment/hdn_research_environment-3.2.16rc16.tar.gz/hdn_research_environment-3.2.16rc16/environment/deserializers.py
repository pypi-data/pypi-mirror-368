import logging
from typing import Iterable, Optional, List

from django.apps import apps
from environment.api_types import (
    RawServiceErrorsData,
    RawWorkspacesData,
    RawSharedWorkspacesData,
    RawWorkbenchesData,
    ServiceErrorResponse,
    WorkspaceResponse,
    SharedWorkspaceResponse,
    WorkbenchResponse,
)

from environment.entities import (
    EntityScaffolding,
    EnvironmentStatus,
    EnvironmentType,
    Region,
    ResearchEnvironment,
    ResearchWorkspace,
    Workflow,
    WorkflowStatus,
    WorkflowType,
    WorkspaceStatus,
    SharedWorkspace,
    SharedBucket,
    SharedBucketObject,
    WorkspaceType,
    QuotaInfo,
    CloudRole,
    DatasetsMonitoringEntry,
    ServiceError,
)

PublishedProject = apps.get_model("project", "PublishedProject")

logger = logging.getLogger(__name__)


def _check_billing_accessibility(billing_info: dict, user_billing_accounts: list = None) -> tuple[bool, str]:
    """
    Check if the billing account is accessible by the user.
    Returns (is_accessible, reason_if_not_accessible)
    """
    billing_account_id = billing_info.get("billing_account_id")
    billing_enabled = billing_info.get("billing_enabled", False)
    
    if not billing_account_id:
        return False, "No billing account connected"
    
    if not billing_enabled:
        return False, "Billing account is closed or inactive"
    
    # Check if user has access to this billing account
    if user_billing_accounts:
        accessible_billing_ids = [acc.get("id") for acc in user_billing_accounts]
        if billing_account_id not in accessible_billing_ids:
            return False, "Billing account access revoked"
    
    return True, None


def _check_workspace_accessibility(
    billing_info: dict, 
    workbenches: list, 
    projects: Iterable[PublishedProject], 
    user_billing_accounts: list = None
) -> tuple[bool, str]:
    """
    Check overall workspace accessibility including billing and project access.
    Returns (is_accessible, reason_if_not_accessible)
    """
    # First check billing accessibility
    billing_accessible, billing_reason = _check_billing_accessibility(billing_info, user_billing_accounts)
    
    # Check if any workbenches have inaccessible projects
    project_access_issues = []
    for workbench in workbenches:
        if workbench.get("type") == "Workbench":
            dataset_id = workbench.get("dataset_identifier")
            if dataset_id:
                project = _get_project_for_environment(dataset_id, projects)
                if not project:
                    project_access_issues.append(f"Dataset '{dataset_id}' access revoked")
    
    # Determine overall accessibility and reason
    if not billing_accessible and project_access_issues:
        return False, f"{billing_reason}; {'; '.join(project_access_issues)}"
    if not billing_accessible:
        return False, billing_reason
    if project_access_issues:
        return False, "; ".join(project_access_issues)
    
    return True, None


def _project_data_group(project: PublishedProject) -> str:
    # HACK: Use the slug and version to calculate the dataset group.
    # The result has to match the patterns for:
    # - Service Account ID: must start with a lower case letter, followed by one or more lower case alphanumerical characters that can be separated by hyphens
    # - Role ID: can only include letters, numbers, full stops and underscores
    #
    # Potential collisions may happen:
    # { slug: some-project, version: 1.1.0 } => someproject110
    # { slug: some-project1, version: 1.0 }  => someproject110
    return "".join(c for c in project.slug + project.version if c.isalnum())


def deserialize_research_environments(
    workbenches: RawWorkbenchesData,
    gcp_project_id: str,
    region: Region,
    projects: Iterable[PublishedProject],
) -> Iterable[ResearchEnvironment]:
    environments = []
    for workbench in workbenches:
        # Note: In actual API responses, type field differentiates workbenches from scaffolding
        # For now, we'll process all items as workbenches since they match WorkbenchResponse structure
        workbench_service_errors = deserialize_service_errors(workbench.get("service_errors", []))
        environments.append(
                ResearchEnvironment(
                    gcp_identifier=workbench["gcp_identifier"],
                    dataset_identifier=workbench["dataset_identifier"],
                    url=workbench.get("url"),
                    workspace_name=gcp_project_id,
                    status=EnvironmentStatus(workbench["status"]),
                    cpu=workbench["cpu"],
                    memory=workbench["memory"],
                    region=region,
                    type=EnvironmentType(workbench["workbench_type"]),
                    machine_type=workbench["machine_type"],
                    disk_size=workbench.get("disk_size"),
                    project=_get_project_for_environment(
                        workbench["dataset_identifier"], projects
                    ),
                    gpu_accelerator_type=workbench.get("gpu_accelerator_type"),
                    service_account_name=workbench["service_account_name"],
                    workbench_owner_username=workbench["workbench_owner_username"],
                    service_errors=workbench_service_errors,
                )
            )
        # Note: Scaffolding handling would be added here if needed
    
    return environments


def deserialize_workflow_details(workflow_data: dict) -> Workflow:
    return Workflow(
        id=workflow_data["id"],
        type=WorkflowType(workflow_data["build_type"]),
        status=WorkflowStatus(workflow_data["status"]),
        error_information=workflow_data["error"],
        workspace_id=workflow_data["workspace_id"],
    )


def deserialize_service_errors(service_errors_data: RawServiceErrorsData) -> List[ServiceError]:
    service_errors = []
    # Handle case where service_errors_data might be None
    if not service_errors_data:
        return service_errors
        
    for error in service_errors_data:
        error_obj = ServiceError(
            error_type=error.get("error_type", "unknown"),
            message=error.get("message", ""),
            resource_id=error.get("resource_id", ""),
            service_name=error.get("service_name", ""),
            details=error.get("details"),
            can_retry=error.get("can_retry", False),
        )
        service_errors.append(error_obj)
    
    return service_errors


def deserialize_workspace_details(
    data: WorkspaceResponse, projects: Iterable[PublishedProject], user_billing_accounts: list = None
) -> ResearchWorkspace:
    # Handle missing or invalid billing_info gracefully
    billing_info = data.get("billing_info")
    if not billing_info or not isinstance(billing_info, dict):
        billing_info = {
            "billing_account_id": None,
            "billing_enabled": False
        }
    
    workspace_accessible, access_denial_reason = _check_workspace_accessibility(
        billing_info, data["workbenches"], projects, user_billing_accounts
    )
    
    service_errors = deserialize_service_errors(data.get("service_errors", []))
    
    # Safely extract billing account ID
    billing_account_id = billing_info.get("billing_account_id")
    
    return ResearchWorkspace(
        region=Region(data["region"]),
        gcp_project_id=data["gcp_project_id"],
        gcp_billing_id=billing_account_id,
        status=WorkspaceStatus(data["status"]),
        is_owner=data["is_owner"],
        workbenches=deserialize_research_environments(
            data["workbenches"],
            data["gcp_project_id"],
            Region(data["region"]),
            projects,
        ),
        is_accessible=workspace_accessible,
        access_denial_reason=access_denial_reason,
        service_errors=service_errors,
    )


def deserialize_shared_bucket_details(buckets_data: List[dict]) -> Iterable[SharedBucket]:
    return [
        SharedBucket(
            name=bucket["bucket_name"],
            is_owner=bucket.get("is_owner", False),
            is_admin=bucket.get("is_admin", False),
        )
        for bucket in buckets_data
    ]


def _check_shared_workspace_accessibility(
    billing_info: dict, 
    service_errors: list,
    user_billing_accounts: list = None
) -> tuple[bool, str]:
    """
    Check shared workspace accessibility including billing and service errors.
    Returns (is_accessible, reason_if_not_accessible)
    """
    # First check billing accessibility
    billing_accessible, billing_reason = _check_billing_accessibility(billing_info, user_billing_accounts)
    
    # Check for critical service errors
    critical_errors = ["billing_disabled", "permission_denied", "not_found"]
    service_error_issues = []
    
    for error in service_errors:
        error_type = error.get("error_type", "")
        error_message = error.get("message", "")
        
        # Check for billing-related errors in message content even if type isn't set correctly
        if (error_type in critical_errors or 
            "billing" in error_message.lower() or 
            "disabled" in error_message.lower() or
            "absent" in error_message.lower()):
            service_error_issues.append(f"Service issue: {error_message or error_type}")
    
    # Determine overall accessibility and reason
    if not billing_accessible and service_error_issues:
        return False, f"{billing_reason}; {'; '.join(service_error_issues)}"
    if not billing_accessible:
        return False, billing_reason
    if service_error_issues:
        return False, "; ".join(service_error_issues)
    
    return True, None


def deserialize_shared_workspace_details(data: SharedWorkspaceResponse, user_billing_accounts: list = None) -> SharedWorkspace:
    service_errors = deserialize_service_errors(data.get("service_errors", []))
    
    # Handle missing or invalid billing_info gracefully
    billing_info = data.get("billing_info")
    if not billing_info or not isinstance(billing_info, dict):
        billing_info = {
            "billing_account_id": None,
            "billing_enabled": False
        }
    
    workspace_accessible, access_denial_reason = _check_shared_workspace_accessibility(
        billing_info, service_errors, user_billing_accounts
    )
    
    # Safely extract billing account ID
    billing_account_id = billing_info.get("billing_account_id")
    
    return SharedWorkspace(
        gcp_project_id=data["gcp_project_id"],
        gcp_billing_id=billing_account_id,
        status=WorkspaceStatus(data["status"]),
        buckets=deserialize_shared_bucket_details(data["buckets"]),
        is_owner=data["is_owner"],
        is_accessible=workspace_accessible,
        access_denial_reason=access_denial_reason,
        service_errors=service_errors,
    )


def deserialize_entity_scaffolding(data: dict) -> EntityScaffolding:
    return EntityScaffolding(
        gcp_project_id=data["gcp_project_id"], status=EnvironmentStatus(data["status"])
    )


def deserialize_workspaces(
    data: RawWorkspacesData, projects: Iterable[PublishedProject], user_billing_accounts: list
) -> Iterable[ResearchWorkspace]:
    return [
        deserialize_workspace_details(workspace_data, projects, user_billing_accounts)
        for workspace_data in data
        # Note: Type checking removed as we now have proper typed data
    ]


def deserialize_shared_workspaces(data: RawSharedWorkspacesData, user_billing_accounts: list) -> Iterable[SharedWorkspace]:
    return [
        deserialize_shared_workspace_details(workspace_data, user_billing_accounts)
        for workspace_data in data
        # Note: Type checking removed as we now have proper typed data
    ]


def _get_project_for_environment(
    dataset_identifier: str,
    projects: Iterable[PublishedProject],
) -> Optional[PublishedProject]:
    try:
        return next(
            iter(
                project
                for project in projects
                if _project_data_group(project) == dataset_identifier
            )
        )
    except StopIteration:
        return None


def deserialize_shared_bucket_objects(data: dict) -> Iterable[SharedBucketObject]:
    return [
        SharedBucketObject(
            type=bucket_object["type"],
            name=bucket_object["name"],
            size=bucket_object["size"],
            modification_time=bucket_object["modification_time"],
            full_path=bucket_object["full_path"],
        )
        for bucket_object in data
    ]


def deserialize_quotas(data) -> Iterable[QuotaInfo]:
    return [
        QuotaInfo(
            metric_name=quota["metric_name"],
            limit=quota["limit"],
            usage=quota["usage"],
            usage_percentage=(quota["usage"] / quota["limit"]) * 100,
        )
        for quota in data
    ]


def deserialize_cloud_roles(data: dict) -> Iterable[CloudRole]:
    return [
        CloudRole(
            full_name=role_object["full_name"],
            title=role_object["title"],
            description=role_object["description"],
        )
        for role_object in data
    ]


def deserialize_datasets_monitoring_data(data) -> Iterable[DatasetsMonitoringEntry]:
    return [
        DatasetsMonitoringEntry(
            dataset_identifier=entry["dataset_identifier"],
            instance_type=entry["instance_type"],
            total_time=entry["total_time"],
            user_email=entry["user_email"],
        )
        for entry in data
    ]
