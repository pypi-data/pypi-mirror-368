"""High-level EventBridge API for AWS event bus operations."""

import logging
from typing import Dict, List, Optional

from chainsaws.aws.eventbridge._eventbridge_internal import EventBridge
from chainsaws.aws.eventbridge.eventbridge_models import (
    CreateRuleResponse,
    EventBridgeAPIConfig,
    EventBusResponse,
    EventPattern,
    PutEventsRequestEntry,
    PutEventsResponse,
    PutTargetsResponse,
    Target,
)
from chainsaws.aws.shared import session

logger = logging.getLogger(__name__)


class EventBridgeAPI:
    """High-level EventBridge API for AWS event bus operations."""

    def __init__(self, config: Optional[EventBridgeAPIConfig] = None) -> None:
        """Initialize EventBridge client.

        Args:
            config: Optional EventBridge configuration

        """
        self.config = config or EventBridgeAPIConfig()
        self.boto3_session = session.get_boto_session(
            self.config.credentials if self.config.credentials else None,
        )
        self.eventbridge = EventBridge(
            boto3_session=self.boto3_session,
            config=config,
        )

    def create_event_bus(
        self,
        name: str,
        tags: Optional[Dict[str, str]] = None,
        event_source_name: Optional[str] = None,
    ) -> EventBusResponse:
        """Create an event bus.

        Args:
            name: Event bus name
            tags: Optional tags to attach to the event bus
            event_source_name: Optional partner event source name

        Returns:
            EventBusResponse containing event bus details

        Examples:
            >>> eventbridge = EventBridgeAPI()
            >>> # Create a custom event bus
            >>> bus = eventbridge.create_event_bus("my-app-events")
            >>> # Create a tagged event bus
            >>> bus = eventbridge.create_event_bus(
            ...     "my-app-events",
            ...     tags={"Environment": "prod", "Team": "platform"}
            ... )

        """
        return self.eventbridge.create_event_bus(name, tags, event_source_name)

    def delete_event_bus(self, name: str) -> None:
        """Delete an event bus.

        Args:
            name: Event bus name to delete

        Examples:
            >>> eventbridge = EventBridgeAPI()
            >>> eventbridge.delete_event_bus("my-app-events")

        """
        self.eventbridge.delete_event_bus(name)

    def list_event_buses(self) -> List[EventBusResponse]:
        """List all event buses.

        Returns:
            List of EventBusResponse containing event bus details

        Examples:
            >>> eventbridge = EventBridgeAPI()
            >>> buses = eventbridge.list_event_buses()
            >>> for bus in buses:
            ...     print(f"Bus: {bus.name}, ARN: {bus.arn}")

        """
        return self.eventbridge.list_event_buses()

    def put_events(
        self,
        entries: List[PutEventsRequestEntry],
        event_bus_name: Optional[str] = None,
    ) -> PutEventsResponse:
        """Send events to EventBridge.

        Args:
            entries: List of event entries to send
            event_bus_name: Optional event bus name

        Returns:
            PutEventsResponse containing results

        Examples:
            >>> eventbridge = EventBridgeAPI()
            >>> response = eventbridge.put_events([
            ...     PutEventsRequestEntry(
            ...         source="com.myapp",
            ...         detail_type="UserSignup",
            ...         detail={"userId": "123", "email": "user@example.com"}
            ...     )
            ... ])

        """
        return self.eventbridge.put_events(entries, event_bus_name)

    def create_rule(
        self,
        name: str,
        event_pattern: Optional[EventPattern] = None,
        schedule_expression: Optional[str] = None,
        event_bus_name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> CreateRuleResponse:
        """Create an EventBridge rule.

        Args:
            name: Rule name
            event_pattern: Optional event pattern
            schedule_expression: Optional schedule expression
            event_bus_name: Optional event bus name
            description: Optional rule description

        Returns:
            CreateRuleResponse containing rule details

        Examples:
            >>> eventbridge = EventBridgeAPI()
            >>> # Create a rule with event pattern
            >>> pattern = EventPattern(
            ...     source=["aws.s3"],
            ...     detail_type=["Object Created"],
            ...     detail={"bucket": {"name": ["my-bucket"]}}
            ... )
            >>> rule = eventbridge.create_rule(
            ...     name="s3-object-created",
            ...     event_pattern=pattern
            ... )

        """
        if schedule_expression:
            logger.warning(
                "You are using a schedule expression. Consider using SchedulerAPI instead."
            )

        pattern_dict = event_pattern.to_dict() if event_pattern else None
        return self.eventbridge.create_rule(
            name=name,
            event_pattern=pattern_dict,
            schedule_expression=schedule_expression,
            event_bus_name=event_bus_name,
            description=description,
        )

    def put_targets(
        self,
        rule: str,
        targets: List[Target],
        event_bus_name: Optional[str] = None,
    ) -> PutTargetsResponse:
        """Add or update targets for an EventBridge rule.

        Args:
            rule: Rule name
            targets: List of targets
            event_bus_name: Optional event bus name

        Returns:
            PutTargetsResponse containing results

        Examples:
            >>> eventbridge = EventBridgeAPI()
            >>> response = eventbridge.put_targets(
            ...     rule="s3-object-created",
            ...     targets=[
            ...         Target(
            ...             id="process-upload",
            ...             arn="arn:aws:lambda:region:account:function:process-upload"
            ...         )
            ...     ]
            ... )

        """
        return self.eventbridge.put_targets(rule, targets, event_bus_name)

    def enable_rule(self, name: str, event_bus_name: Optional[str] = None) -> None:
        """Enable a rule.

        Args:
            name: Rule name
            event_bus_name: Optional event bus name

        Examples:
            >>> eventbridge = EventBridgeAPI()
            >>> eventbridge.enable_rule("my-rule")

        """
        self.eventbridge.enable_rule(name, event_bus_name)

    def disable_rule(self, name: str, event_bus_name: Optional[str] = None) -> None:
        """Disable a rule.

        Args:
            name: Rule name
            event_bus_name: Optional event bus name

        Examples:
            >>> eventbridge = EventBridgeAPI()
            >>> eventbridge.disable_rule("my-rule")

        """
        self.eventbridge.disable_rule(name, event_bus_name)
