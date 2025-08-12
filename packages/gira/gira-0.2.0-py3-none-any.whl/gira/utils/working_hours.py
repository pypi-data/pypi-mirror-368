"""Utilities for calculating working hours between timestamps."""

from calendar import day_name
from datetime import date, datetime, time, timedelta
from typing import List, Optional

import pytz

from gira.models.working_hours import WorkingHoursConfig


def calculate_working_hours(
    start_dt: datetime,
    end_dt: datetime,
    config: WorkingHoursConfig
) -> float:
    """
    Calculate working hours between two timestamps.
    
    Args:
        start_dt: Start datetime (timezone-aware)
        end_dt: End datetime (timezone-aware)
        config: Working hours configuration
        
    Returns:
        Number of working hours between the timestamps
    """
    # Convert to configured timezone
    tz = pytz.timezone(config.timezone)
    start_local = start_dt.astimezone(tz)
    end_local = end_dt.astimezone(tz)

    # If end is before start, return 0
    if end_local <= start_local:
        return 0.0

    # Parse working hours
    work_start = time.fromisoformat(config.start_time)
    work_end = time.fromisoformat(config.end_time)
    hours_per_day = config.get_working_hours_per_day()

    # Start with the first day
    current_date = start_local.date()
    end_date = end_local.date()
    total_hours = 0.0

    while current_date <= end_date:
        # Check if it's a working day
        day_name_str = day_name[current_date.weekday()]
        if config.is_working_day(day_name_str) and not config.is_holiday(current_date):
            # Calculate hours for this day
            if current_date == start_local.date() and current_date == end_local.date():
                # Same day - calculate hours between start and end
                day_hours = _calculate_same_day_hours(
                    start_local.time(), end_local.time(), work_start, work_end
                )
            elif current_date == start_local.date():
                # First day - from start time to end of work day
                day_hours = _calculate_same_day_hours(
                    start_local.time(), work_end, work_start, work_end
                )
            elif current_date == end_local.date():
                # Last day - from start of work day to end time
                day_hours = _calculate_same_day_hours(
                    work_start, end_local.time(), work_start, work_end
                )
            else:
                # Full working day
                day_hours = hours_per_day

            total_hours += day_hours

        # Move to next day
        current_date += timedelta(days=1)

    return total_hours


def _calculate_same_day_hours(
    start_time: time,
    end_time: time,
    work_start: time,
    work_end: time
) -> float:
    """Calculate working hours within a single day."""
    # Clamp times to working hours
    actual_start = max(start_time, work_start)
    actual_end = min(end_time, work_end)

    # If end is before start (no overlap with working hours), return 0
    if actual_end <= actual_start:
        return 0.0

    # Calculate hours
    start_minutes = actual_start.hour * 60 + actual_start.minute
    end_minutes = actual_end.hour * 60 + actual_end.minute

    return (end_minutes - start_minutes) / 60.0


def format_working_hours(hours: float) -> str:
    """Format working hours for display."""
    if hours < 1:
        return f"{int(hours * 60)}m"
    elif hours < 8:
        return f"{hours:.1f}h"
    else:
        # Convert to days (assuming 8-hour work day)
        days = hours / 8
        if days < 1:
            return f"{hours:.1f}h"
        else:
            return f"{days:.1f}d ({hours:.0f}h)"


def get_next_working_day(
    current_date: date,
    config: WorkingHoursConfig
) -> Optional[date]:
    """Get the next working day after the given date."""
    next_date = current_date + timedelta(days=1)
    max_days = 365  # Prevent infinite loop
    days_checked = 0

    while days_checked < max_days:
        day_name_str = day_name[next_date.weekday()]
        if config.is_working_day(day_name_str) and not config.is_holiday(next_date):
            return next_date
        next_date += timedelta(days=1)
        days_checked += 1

    return None


def get_working_days_between(
    start_date: date,
    end_date: date,
    config: WorkingHoursConfig
) -> int:
    """Count working days between two dates (inclusive)."""
    if end_date < start_date:
        return 0

    current_date = start_date
    working_days = 0

    while current_date <= end_date:
        day_name_str = day_name[current_date.weekday()]
        if config.is_working_day(day_name_str) and not config.is_holiday(current_date):
            working_days += 1
        current_date += timedelta(days=1)

    return working_days


def parse_holidays_from_strings(holiday_strings: List[str]) -> List[date]:
    """Parse holiday strings to date objects."""
    holidays = []
    for holiday_str in holiday_strings:
        try:
            holidays.append(date.fromisoformat(holiday_str))
        except ValueError:
            # Skip invalid dates
            continue
    return holidays
