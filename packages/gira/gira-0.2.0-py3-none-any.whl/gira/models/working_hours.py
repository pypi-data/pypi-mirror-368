"""Working hours configuration model for business hours calculations."""

from typing import List, Optional
from datetime import time, date
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import pytz


class DayOfWeek(str, Enum):
    """Days of the week."""
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class WorkingHoursConfig(BaseModel):
    """Configuration for working hours calculation."""
    
    timezone: str = Field(
        default="UTC",
        description="Timezone for working hours (e.g., 'America/New_York', 'Europe/London')"
    )
    start_time: str = Field(
        default="09:00",
        description="Daily work start time in HH:MM format"
    )
    end_time: str = Field(
        default="17:00",
        description="Daily work end time in HH:MM format"
    )
    working_days: List[DayOfWeek] = Field(
        default_factory=lambda: [
            DayOfWeek.MONDAY,
            DayOfWeek.TUESDAY,
            DayOfWeek.WEDNESDAY,
            DayOfWeek.THURSDAY,
            DayOfWeek.FRIDAY
        ],
        description="List of working days in the week"
    )
    holidays: List[str] = Field(
        default_factory=list,
        description="List of holidays in YYYY-MM-DD format"
    )
    
    @field_validator('timezone')
    def validate_timezone(cls, v):
        """Validate timezone is valid."""
        try:
            pytz.timezone(v)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Unknown timezone: {v}")
        return v
    
    @field_validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        """Validate time format."""
        try:
            time.fromisoformat(v)
        except ValueError:
            raise ValueError(f"Invalid time format: {v}. Use HH:MM format.")
        return v
    
    @field_validator('holidays')
    def validate_holidays(cls, v):
        """Validate holiday date format."""
        for holiday in v:
            try:
                date.fromisoformat(holiday)
            except ValueError:
                raise ValueError(f"Invalid date format: {holiday}. Use YYYY-MM-DD format.")
        return v
    
    def get_working_hours_per_day(self) -> float:
        """Calculate working hours per day."""
        start = time.fromisoformat(self.start_time)
        end = time.fromisoformat(self.end_time)
        
        # Calculate hours difference
        start_minutes = start.hour * 60 + start.minute
        end_minutes = end.hour * 60 + end.minute
        
        return (end_minutes - start_minutes) / 60.0
    
    def is_working_day(self, day_name: str) -> bool:
        """Check if a day is a working day."""
        try:
            day = DayOfWeek(day_name)
            return day in self.working_days
        except ValueError:
            return False
    
    def is_holiday(self, check_date: date) -> bool:
        """Check if a date is a holiday."""
        date_str = check_date.isoformat()
        return date_str in self.holidays
    
    class Config:
        """Pydantic config."""
        use_enum_values = True