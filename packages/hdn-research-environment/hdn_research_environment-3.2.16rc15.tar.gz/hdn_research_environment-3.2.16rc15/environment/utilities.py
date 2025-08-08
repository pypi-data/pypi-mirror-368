from typing import Callable, Iterator, Optional, Tuple, TypeVar

from django.db.models import Model
from environment.entities import ServiceError

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

User = Model


def user_has_cloud_identity(user: User) -> bool:
    return hasattr(user, "cloud_identity")


def user_has_access_billing_account(billing_accounts_list) -> bool:
    return bool(billing_accounts_list)


def user_workspace_setup_done(user: User) -> bool:
    if not user_has_cloud_identity(user):
        return False
    return user.cloud_identity.initial_workspace_setup_done


def inner_join_iterators(
    key_left: Callable[[T], V],
    left: Iterator[T],
    key_right: Callable[[U], V],
    right: Iterator[U],
) -> Iterator[Tuple[T, U]]:
    right_dict = {key_right(element): element for element in right}
    return [
        (element, right_dict[key_left(element)])
        for element in left
        if key_left(element) in right_dict
    ]


def left_join_iterators(
    key_left: Callable[[T], V],
    left: Iterator[T],
    key_right: Callable[[U], V],
    right: Iterator[U],
) -> Iterator[Tuple[T, Optional[U]]]:
    right_dict = {key_right(element): element for element in right}
    return [(element, right_dict.get(key_left(element))) for element in left]


def has_service_errors(workspace_or_workbench) -> bool:
    """Check if workspace or workbench has service errors."""
    return (
        workspace_or_workbench.service_errors is not None 
        and len(workspace_or_workbench.service_errors) > 0
    )


def has_billing_error(workspace_or_workbench) -> bool:
    """Check if workspace or workbench has billing-related errors."""
    if not has_service_errors(workspace_or_workbench):
        return False
    return any(error.error_type == "billing_disabled" for error in workspace_or_workbench.service_errors)


def has_api_error(workspace_or_workbench) -> bool:
    """Check if workspace or workbench has API-related errors."""
    if not has_service_errors(workspace_or_workbench):
        return False
    return any(error.error_type == "api_not_enabled" for error in workspace_or_workbench.service_errors)


def has_permission_error(workspace_or_workbench) -> bool:
    """Check if workspace or workbench has permission-related errors."""
    if not has_service_errors(workspace_or_workbench):
        return False
    return any(error.error_type == "permission_denied" for error in workspace_or_workbench.service_errors)


def get_billing_link(workspace_id: str) -> str:
    """Generate billing enable link for a workspace."""
    return f"https://console.developers.google.com/billing/enable?project={workspace_id}"


def format_error_message(error: ServiceError) -> str:
    """Format error message for display in templates."""
    if error.error_type == "billing_disabled":
        return f"⚠️ Billing disabled: {error.message}"
    elif error.error_type == "api_not_enabled":
        return f"⏳ APIs enabling: {error.service_name} APIs are being enabled"
    elif error.error_type == "permission_denied":
        return f"🚫 Access denied: {error.message}"
    elif error.error_type == "quota_exceeded":
        return f"📊 Quota exceeded: {error.message}"
    elif error.error_type == "not_found":
        return f"❓ Resource not found: {error.message}"
    else:
        return f"❌ Error: {error.message}"


def get_error_action_text(error: ServiceError) -> Optional[str]:
    """Get action text for error types that have user actions."""
    if error.error_type == "billing_disabled":
        return "Enable billing"
    elif error.error_type == "quota_exceeded" and error.can_retry:
        return "Retry later"
    return None


def get_error_action_link(error: ServiceError) -> Optional[str]:
    """Get action link for error types that have user actions."""
    if error.error_type == "billing_disabled":
        return get_billing_link(error.resource_id)
    return None


def get_error_css_class(error: ServiceError) -> str:
    """Get CSS class for error type."""
    error_type_map = {
        "billing_disabled": "error-billing",
        "api_not_enabled": "error-api",
        "permission_denied": "error-permission",
        "quota_exceeded": "error-quota",
        "not_found": "error-permission",
        "unknown": "error-unknown",
    }
    return error_type_map.get(error.error_type, "error-unknown")


def workspace_is_functional(workspace) -> bool:
    """Check if workspace is functional (no critical errors)."""
    if not has_service_errors(workspace):
        return True
    
    # Consider workspace non-functional if it has billing or permission errors
    critical_errors = ["billing_disabled", "permission_denied", "not_found"]
    return not any(error.error_type in critical_errors for error in workspace.service_errors)


def workbench_is_accessible(workbench) -> bool:
    """Check if workbench is accessible (no service errors)."""
    return not has_service_errors(workbench)
