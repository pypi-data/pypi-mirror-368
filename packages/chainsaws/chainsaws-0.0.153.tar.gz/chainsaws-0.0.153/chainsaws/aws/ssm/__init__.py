"""AWS Systems Manager (SSM) wrapper.

This package provides a high-level interface for AWS Systems Manager operations,
implementing best practices and providing intuitive access to SSM features.

Features:
- Parameter Store management
- Session Manager operations
- Patch Management
- State Manager
- Maintenance Windows
- Inventory Management
- Run Command execution
- Automation execution

Example:
    ```python
    from chainsaws.aws.ssm import SSMAPI

    # Initialize SSM client
    ssm = SSMAPI()

    # Store a secure parameter
    ssm.put_parameter(
        name="/prod/db/password",
        value="secret123",
        param_type="SecureString"
    )

    # Start a session with an EC2 instance
    session = ssm.start_session(
        instance_id="i-1234567890abcdef0",
        reason="Maintenance"
    )

    # Create a maintenance window
    window = ssm.create_maintenance_window(
        name="WeeklyPatching",
        schedule="cron(0 0 ? * SUN *)",
        duration=4,
        cutoff=1
    )
    ```

"""

from chainsaws.aws.ssm.ssm import SSMAPI
from chainsaws.aws.ssm.ssm_models import (
    AutomationExecution,
    AutomationExecutionConfig,
    CommandConfig,
    CommandInvocation,
    InventoryConfig,
    MaintenanceTask,
    MaintenanceWindow,
    MaintenanceWindowConfig,
    Parameter,
    ParameterConfig,
    PatchBaselineConfig,
    PatchSummary,
    SessionConfig,
    SessionDetails,
    SSMAPIConfig,
    StateAssociation,
    StateConfig,
)

__all__ = [
    "SSMAPI",
    "AutomationExecution",
    "AutomationExecutionConfig",
    "CommandConfig",
    "CommandInvocation",
    "InventoryConfig",
    "MaintenanceTask",
    "MaintenanceWindow",
    "MaintenanceWindowConfig",
    "Parameter",
    "ParameterConfig",
    "PatchBaselineConfig",
    "PatchSummary",
    "SSMAPIConfig",
    "SessionConfig",
    "SessionDetails",
    "StateAssociation",
    "StateConfig",
]
