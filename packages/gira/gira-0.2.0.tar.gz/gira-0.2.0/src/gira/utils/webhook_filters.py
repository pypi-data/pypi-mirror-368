"""Advanced webhook filtering system for Gira.

Provides sophisticated filtering capabilities for webhook events
using query-based expressions and conditional logic.
"""

import re
from typing import Dict, Any, List, Optional


class WebhookFilter:
    """Advanced webhook filter with query language support."""
    
    def __init__(self, filter_expression: str):
        self.expression = filter_expression.strip()
        self.parsed_conditions = self._parse_expression(self.expression)
    
    def _parse_expression(self, expression: str) -> List[Dict[str, Any]]:
        """Parse filter expression into structured conditions."""
        conditions = []
        
        if not expression:
            return conditions
        
        # Handle OR operations
        or_parts = [part.strip() for part in expression.split(" OR ")]
        
        for part in or_parts:
            # Handle AND operations within each OR part
            and_conditions = []
            and_parts = [p.strip() for p in part.split(" AND ")]
            
            for and_part in and_parts:
                condition = self._parse_condition(and_part)
                if condition:
                    and_conditions.append(condition)
            
            if and_conditions:
                conditions.append({
                    "type": "AND" if len(and_conditions) > 1 else "SINGLE",
                    "conditions": and_conditions
                })
        
        return conditions
    
    def _parse_condition(self, condition: str) -> Optional[Dict[str, Any]]:
        """Parse a single condition like 'priority:high' or 'type:bug'."""
        # Handle field:value patterns
        field_value_match = re.match(r'^(\w+):(.+)$', condition.strip())
        if field_value_match:
            field, value = field_value_match.groups()
            return {
                "type": "equals",
                "field": field.lower(),
                "value": value.strip()
            }
        
        # Handle contains patterns like 'labels:security'
        contains_match = re.match(r'^(\w+)~(.+)$', condition.strip())
        if contains_match:
            field, value = contains_match.groups()
            return {
                "type": "contains",
                "field": field.lower(),
                "value": value.strip()
            }
        
        # Handle not equals patterns like 'status!=done'
        not_equals_match = re.match(r'^(\w+)!=(.+)$', condition.strip())
        if not_equals_match:
            field, value = not_equals_match.groups()
            return {
                "type": "not_equals",
                "field": field.lower(),
                "value": value.strip()
            }
        
        return None
    
    def matches(self, payload: Dict[str, Any]) -> bool:
        """Check if the payload matches the filter conditions."""
        if not self.parsed_conditions:
            return True  # No filter means match all
        
        # Extract ticket data from payload
        ticket_data = payload.get("data", {}).get("ticket", {})
        
        # Check if any OR condition group matches
        for condition_group in self.parsed_conditions:
            if self._matches_condition_group(condition_group, ticket_data, payload):
                return True
        
        return False
    
    def _matches_condition_group(self, condition_group: Dict[str, Any], 
                                ticket_data: Dict[str, Any], 
                                full_payload: Dict[str, Any]) -> bool:
        """Check if a condition group (AND or SINGLE) matches."""
        conditions = condition_group["conditions"]
        
        if condition_group["type"] == "SINGLE":
            return self._matches_single_condition(conditions[0], ticket_data, full_payload)
        
        # AND group - all conditions must match
        for condition in conditions:
            if not self._matches_single_condition(condition, ticket_data, full_payload):
                return False
        
        return True
    
    def _matches_single_condition(self, condition: Dict[str, Any], 
                                 ticket_data: Dict[str, Any], 
                                 full_payload: Dict[str, Any]) -> bool:
        """Check if a single condition matches."""
        condition_type = condition["type"]
        field = condition["field"]
        expected_value = condition["value"]
        
        # Get the actual value from ticket data
        actual_value = self._get_field_value(field, ticket_data, full_payload)
        
        if condition_type == "equals":
            return str(actual_value).lower() == expected_value.lower()
        
        elif condition_type == "not_equals":
            return str(actual_value).lower() != expected_value.lower()
        
        elif condition_type == "contains":
            if isinstance(actual_value, list):
                return any(expected_value.lower() in str(item).lower() for item in actual_value)
            else:
                return expected_value.lower() in str(actual_value).lower()
        
        return False
    
    def _get_field_value(self, field: str, ticket_data: Dict[str, Any], 
                        full_payload: Dict[str, Any]) -> Any:
        """Get field value from ticket data or payload."""
        # Handle special fields
        if field == "event":
            return full_payload.get("event", "")
        
        if field == "project":
            return full_payload.get("project", "")
        
        # Handle change-related fields
        if field.startswith("changed_"):
            change_field = field[8:]  # Remove "changed_" prefix
            changes = full_payload.get("data", {}).get("changes", {})
            return change_field in changes
        
        # Handle ticket fields
        field_mapping = {
            "id": "id",
            "title": "title",
            "description": "description",
            "status": "status",
            "type": "type",
            "priority": "priority",
            "assignee": "assignee",
            "reporter": "reporter",
            "labels": "labels",
            "epic": "epic_id",
            "epic_id": "epic_id",
            "sprint": "sprint_id",
            "sprint_id": "sprint_id",
            "story_points": "story_points",
            "blocked_by": "blocked_by",
            "blocks": "blocks"
        }
        
        mapped_field = field_mapping.get(field, field)
        return ticket_data.get(mapped_field, "")


class WebhookFilterManager:
    """Manages webhook filtering for multiple endpoints."""
    
    @staticmethod
    def filter_endpoints_for_event(endpoints: List[Dict[str, Any]], 
                                  event_type: str, 
                                  payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter endpoints that should receive the event."""
        matching_endpoints = []
        
        for endpoint in endpoints:
            if not endpoint.get("enabled", True):
                continue
            
            # Check event type filter
            events = endpoint.get("events", ["*"])
            if "*" not in events and event_type not in events:
                continue
            
            # Check query-based filter
            filter_expression = endpoint.get("filter", "")
            if filter_expression:
                webhook_filter = WebhookFilter(filter_expression)
                if not webhook_filter.matches(payload):
                    continue
            
            matching_endpoints.append(endpoint)
        
        return matching_endpoints
    
    @staticmethod
    def validate_filter_expression(expression: str) -> tuple[bool, Optional[str]]:
        """Validate a filter expression and return (is_valid, error_message)."""
        try:
            if not expression.strip():
                return True, None
            
            webhook_filter = WebhookFilter(expression)
            
            # Check if we could parse any conditions
            if not webhook_filter.parsed_conditions and expression.strip():
                return False, "Could not parse any valid conditions from the expression"
            
            return True, None
        
        except Exception as e:
            return False, f"Invalid filter expression: {str(e)}"
    
    @staticmethod
    def get_supported_fields() -> Dict[str, str]:
        """Get list of supported filter fields with descriptions."""
        return {
            "event": "Event type (e.g., ticket_created, ticket_moved)",
            "project": "Project name",
            "id": "Ticket ID",
            "title": "Ticket title",
            "description": "Ticket description", 
            "status": "Ticket status (e.g., todo, in_progress, done)",
            "type": "Ticket type (e.g., task, bug, feature)",
            "priority": "Ticket priority (e.g., low, medium, high)",
            "assignee": "Assigned user email",
            "reporter": "Reporter user email",
            "labels": "Ticket labels (use ~ for contains)",
            "epic": "Epic ID",
            "sprint": "Sprint ID",
            "story_points": "Story points value",
            "changed_status": "True if status changed (for update events)"
        }
    
    @staticmethod
    def get_filter_examples() -> List[Dict[str, str]]:
        """Get example filter expressions."""
        return [
            {
                "expression": "priority:high",
                "description": "Only high priority tickets"
            },
            {
                "expression": "type:bug OR priority:high",
                "description": "Bugs or high priority tickets"
            },
            {
                "expression": "status:done AND priority:high",
                "description": "High priority tickets that are completed"
            },
            {
                "expression": "labels~security",
                "description": "Tickets containing 'security' in labels"
            },
            {
                "expression": "assignee:john@company.com OR reporter:jane@company.com",
                "description": "Tickets assigned to John or reported by Jane"
            },
            {
                "expression": "type:bug AND status!=done",
                "description": "Open bugs (not done)"
            },
            {
                "expression": "event:ticket_moved AND changed_status",
                "description": "Only status change events"
            }
        ]