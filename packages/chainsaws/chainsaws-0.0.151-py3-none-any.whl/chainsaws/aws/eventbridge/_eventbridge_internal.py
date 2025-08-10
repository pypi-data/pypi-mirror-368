"""Internal implementation of EventBridge API."""

import logging
from typing import Any, Dict, List, Optional

import boto3

from chainsaws.aws.eventbridge.eventbridge_models import (
    CreateRuleResponse,
    EventBridgeAPIConfig,
    EventBusResponse,
    PutEventsRequestEntry,
    PutEventsResponse,
    PutTargetsResponse,
    Target,
)

logger = logging.getLogger(__name__)


class EventBridge:
    """Internal EventBridge implementation."""

    def __init__(
        self,
        boto3_session: boto3.Session,
        config: Optional[EventBridgeAPIConfig] = None,
    ) -> None:
        """Initialize EventBridge client.

        Args:
            boto3_session: Boto3 session
            config: Optional EventBridge configuration

        """
        self.config = config or EventBridgeAPIConfig()
        self.client = boto3_session.client(
            "events",
            region_name=self.config.region_name,
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
            tags: Optional tags
            event_source_name: Optional partner event source name

        Returns:
            EventBusResponse containing event bus details

        """
        kwargs: Dict[str, Any] = {"Name": name}
        if tags:
            kwargs["Tags"] = [{"Key": k, "Value": v} for k, v in tags.items()]
        if event_source_name:
            kwargs["EventSourceName"] = event_source_name

        response = self.client.create_event_bus(**kwargs)
        return EventBusResponse(
            name=name,
            arn=response["EventBusArn"],
        )

    def delete_event_bus(self, name: str) -> None:
        """Delete an event bus.

        Args:
            name: Event bus name to delete

        """
        self.client.delete_event_bus(Name=name)

    def list_event_buses(self) -> List[EventBusResponse]:
        """List all event buses.

        Returns:
            List of EventBusResponse containing event bus details

        """
        response = self.client.list_event_buses()
        return [
            EventBusResponse(
                name=bus["Name"],
                arn=bus["Arn"],
                policy=bus.get("Policy"),
            )
            for bus in response["EventBuses"]
        ]

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

        """
        request_entries = []
        for entry in entries:
            event_entry = {
                "Detail": str(entry.detail),
                "DetailType": entry.detail_type,
                "Source": entry.source,
            }
            if entry.event_bus_name:
                event_entry["EventBusName"] = entry.event_bus_name
            if entry.resources:
                event_entry["Resources"] = entry.resources
            if entry.time:
                event_entry["Time"] = entry.time
            request_entries.append(event_entry)

        response = self.client.put_events(Entries=request_entries)
        return PutEventsResponse(
            entries=response["Entries"],
            failed_entry_count=response["FailedEntryCount"],
        )

    def create_rule(
        self,
        name: str,
        event_pattern: Optional[Dict[str, Any]] = None,
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

        """
        kwargs: Dict[str, Any] = {"Name": name}

        if event_pattern:
            kwargs["EventPattern"] = str(event_pattern)
        if schedule_expression:
            kwargs["ScheduleExpression"] = schedule_expression
        if event_bus_name:
            kwargs["EventBusName"] = event_bus_name
        if description:
            kwargs["Description"] = description

        response = self.client.put_rule(**kwargs)
        return CreateRuleResponse(
            rule_arn=response["RuleArn"],
            name=name,
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

        """
        kwargs: Dict[str, Any] = {
            "Rule": rule,
            "Targets": [
                {
                    "Id": target.id,
                    "Arn": target.arn,
                    **({"Input": target.input} if target.input else {}),
                    **({"InputPath": target.input_path} if target.input_path else {}),
                    **(
                        {"InputTransformer": target.input_transformer}
                        if target.input_transformer
                        else {}
                    ),
                    **({"RoleArn": target.role_arn} if target.role_arn else {}),
                    **(
                        {"DeadLetterConfig": target.dead_letter_config}
                        if target.dead_letter_config
                        else {}
                    ),
                    **({"RetryPolicy": target.retry_policy} if target.retry_policy else {}),
                }
                for target in targets
            ],
        }

        if event_bus_name:
            kwargs["EventBusName"] = event_bus_name

        response = self.client.put_targets(**kwargs)
        return PutTargetsResponse(
            failed_entry_count=response["FailedEntryCount"],
            failed_entries=response["FailedEntries"],
        )

    def enable_rule(self, name: str, event_bus_name: Optional[str] = None) -> None:
        """Enable a rule.

        Args:
            name: Rule name
            event_bus_name: Optional event bus name

        """
        kwargs: Dict[str, Any] = {"Name": name}
        if event_bus_name:
            kwargs["EventBusName"] = event_bus_name
        self.client.enable_rule(**kwargs)

    def disable_rule(self, name: str, event_bus_name: Optional[str] = None) -> None:
        """Disable a rule.

        Args:
            name: Rule name
            event_bus_name: Optional event bus name

        """
        kwargs: Dict[str, Any] = {"Name": name}
        if event_bus_name:
            kwargs["EventBusName"] = event_bus_name
        self.client.disable_rule(**kwargs)
