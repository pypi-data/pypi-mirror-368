"""Custom fields models for Gira projects."""

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class CustomFieldType(str, Enum):
    """Supported custom field types."""
    
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    DATE = "date"
    ENUM = "enum"
    
    @classmethod
    def from_string(cls, value: str) -> "CustomFieldType":
        """Convert string to enum value."""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(
                f"Invalid custom field type: {value}. "
                f"Must be one of: {', '.join(cls._value2member_map_.keys())}"
            )


class CustomFieldAppliesTo(str, Enum):
    """Entities that custom fields can apply to."""
    
    TICKET = "ticket"
    EPIC = "epic"
    ALL = "all"
    
    @classmethod
    def from_string(cls, value: str) -> "CustomFieldAppliesTo":
        """Convert string to enum value."""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(
                f"Invalid applies_to value: {value}. "
                f"Must be one of: {', '.join(cls._value2member_map_.keys())}"
            )


class CustomFieldDefinition(BaseModel):
    """Definition of a custom field."""
    
    name: str = Field(
        ...,
        pattern=r"^[a-z][a-z0-9_]*$",
        min_length=1,
        max_length=50,
        description="Field name (lowercase, alphanumeric with underscores)"
    )
    display_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable display name"
    )
    type: CustomFieldType = Field(
        ...,
        description="Field data type"
    )
    applies_to: CustomFieldAppliesTo = Field(
        default=CustomFieldAppliesTo.ALL,
        description="Which entities this field applies to"
    )
    required: bool = Field(
        default=False,
        description="Whether this field is required"
    )
    default_value: Optional[Union[str, int, bool]] = Field(
        default=None,
        description="Default value for the field"
    )
    options: Optional[List[str]] = Field(
        default=None,
        description="Valid options for enum fields"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Field description for help text"
    )
    validation_pattern: Optional[str] = Field(
        default=None,
        description="Regex pattern for string field validation"
    )
    min_value: Optional[Union[int, float]] = Field(
        default=None,
        description="Minimum value for integer fields"
    )
    max_value: Optional[Union[int, float]] = Field(
        default=None,
        description="Maximum value for integer fields"
    )
    
    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v: Any) -> CustomFieldType:
        """Validate and convert type to enum."""
        if isinstance(v, str):
            return CustomFieldType.from_string(v)
        return v
    
    @field_validator("applies_to", mode="before")
    @classmethod
    def validate_applies_to(cls, v: Any) -> CustomFieldAppliesTo:
        """Validate and convert applies_to to enum."""
        if isinstance(v, str):
            return CustomFieldAppliesTo.from_string(v)
        return v
    
    @model_validator(mode="after")
    def validate_field_config(self) -> "CustomFieldDefinition":
        """Validate field configuration based on type."""
        # Enum fields must have options
        if self.type == CustomFieldType.ENUM:
            if not self.options or len(self.options) == 0:
                raise ValueError("Enum fields must have at least one option")
            # Ensure options are unique
            if len(set(self.options)) != len(self.options):
                raise ValueError("Enum options must be unique")
        elif self.options is not None:
            # Non-enum fields shouldn't have options
            raise ValueError(f"Options are only valid for enum fields, not {self.type}")
        
        # Integer fields can have min/max values
        if self.type != CustomFieldType.INTEGER:
            if self.min_value is not None or self.max_value is not None:
                raise ValueError("min_value and max_value are only valid for integer fields")
        elif self.min_value is not None and self.max_value is not None:
            if self.min_value > self.max_value:
                raise ValueError("min_value must be less than or equal to max_value")
        
        # String fields can have validation pattern
        if self.type != CustomFieldType.STRING and self.validation_pattern is not None:
            raise ValueError("validation_pattern is only valid for string fields")
        
        # Validate default value matches type
        if self.default_value is not None:
            self._validate_value(self.default_value)
        
        return self
    
    def _validate_value(self, value: Any) -> None:
        """Validate a value against this field's constraints."""
        if value is None:
            if self.required:
                raise ValueError(f"Field '{self.name}' is required")
            return
        
        if self.type == CustomFieldType.STRING:
            if not isinstance(value, str):
                raise ValueError(f"Field '{self.name}' must be a string")
            if self.validation_pattern:
                import re
                if not re.match(self.validation_pattern, value):
                    raise ValueError(
                        f"Field '{self.name}' value '{value}' does not match pattern '{self.validation_pattern}'"
                    )
        
        elif self.type == CustomFieldType.INTEGER:
            if not isinstance(value, int):
                raise ValueError(f"Field '{self.name}' must be an integer")
            if self.min_value is not None and value < self.min_value:
                raise ValueError(f"Field '{self.name}' value {value} is less than minimum {self.min_value}")
            if self.max_value is not None and value > self.max_value:
                raise ValueError(f"Field '{self.name}' value {value} is greater than maximum {self.max_value}")
        
        elif self.type == CustomFieldType.BOOLEAN:
            if not isinstance(value, bool):
                raise ValueError(f"Field '{self.name}' must be a boolean")
        
        elif self.type == CustomFieldType.DATE:
            if not isinstance(value, str):
                raise ValueError(f"Field '{self.name}' must be a date string (ISO format)")
            # Validate ISO date format
            import re
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
                raise ValueError(f"Field '{self.name}' must be in ISO date format (YYYY-MM-DD)")
            # Validate it's a valid date
            from datetime import datetime
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Field '{self.name}' contains invalid date: {value}")
        
        elif self.type == CustomFieldType.ENUM:
            if value not in self.options:
                raise ValueError(
                    f"Field '{self.name}' value '{value}' is not one of: {', '.join(self.options)}"
                )
    
    def validate_value(self, value: Any) -> Any:
        """Validate and potentially transform a value for this field."""
        self._validate_value(value)
        return value
    
    def get_cli_option_name(self) -> str:
        """Get the CLI option name for this field."""
        return f"cf-{self.name.replace('_', '-')}"
    
    def get_cli_help_text(self) -> str:
        """Get help text for CLI option."""
        help_text = self.description or f"Custom field: {self.display_name}"
        
        if self.required:
            help_text += " (required)"
        
        if self.default_value is not None:
            help_text += f" [default: {self.default_value}]"
        
        if self.type == CustomFieldType.ENUM:
            help_text += f" [options: {', '.join(self.options)}]"
        elif self.type == CustomFieldType.INTEGER:
            if self.min_value is not None or self.max_value is not None:
                constraints = []
                if self.min_value is not None:
                    constraints.append(f"min: {self.min_value}")
                if self.max_value is not None:
                    constraints.append(f"max: {self.max_value}")
                help_text += f" [{', '.join(constraints)}]"
        elif self.type == CustomFieldType.DATE:
            help_text += " [format: YYYY-MM-DD]"
        
        return help_text


class CustomFieldsConfig(BaseModel):
    """Configuration for custom fields in a project."""
    
    fields: List[CustomFieldDefinition] = Field(
        default_factory=list,
        description="List of custom field definitions"
    )
    
    def get_fields_for_entity(self, entity_type: str) -> List[CustomFieldDefinition]:
        """Get custom fields that apply to a specific entity type."""
        entity_type_lower = entity_type.lower()
        return [
            field for field in self.fields
            if field.applies_to == CustomFieldAppliesTo.ALL
            or field.applies_to.value == entity_type_lower
        ]
    
    def get_field_by_name(self, name: str) -> Optional[CustomFieldDefinition]:
        """Get a custom field definition by name."""
        for field in self.fields:
            if field.name == name:
                return field
        return None
    
    def validate_custom_fields(self, values: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """Validate custom field values for an entity."""
        applicable_fields = self.get_fields_for_entity(entity_type)
        validated = {}
        
        # Check all applicable fields
        for field in applicable_fields:
            value = values.get(field.name)
            
            # Use default if not provided
            if value is None and field.default_value is not None:
                value = field.default_value
            
            # Validate the value
            if value is not None or field.required:
                validated[field.name] = field.validate_value(value)
        
        # Check for unknown fields
        known_field_names = {f.name for f in applicable_fields}
        for name in values:
            if name not in known_field_names:
                raise ValueError(f"Unknown custom field: {name}")
        
        return validated