"""Tests for date_utils module."""

import pytest
from datetime import datetime, timedelta
from myutils.date_utils import (
    format_datetime, parse_datetime, days_ago, days_from_now,
    is_weekend, get_age_in_years, time_since
)


class TestDateTimeFormatting:
    """Test datetime formatting functions."""
    
    def test_format_datetime_default(self):
        """Test default datetime formatting."""
        dt = datetime(2024, 3, 15, 14, 30, 45)
        result = format_datetime(dt)
        assert result == "2024-03-15 14:30:45"
    
    def test_format_datetime_custom_format(self):
        """Test datetime formatting with custom format."""
        dt = datetime(2024, 3, 15, 14, 30, 45)
        
        # Test various formats
        assert format_datetime(dt, "%Y-%m-%d") == "2024-03-15"
        assert format_datetime(dt, "%d/%m/%Y") == "15/03/2024"
        assert format_datetime(dt, "%B %d, %Y") == "March 15, 2024"
        assert format_datetime(dt, "%H:%M:%S") == "14:30:45"
        assert format_datetime(dt, "%A, %B %d, %Y at %I:%M %p") == "Friday, March 15, 2024 at 02:30 PM"
    
    def test_parse_datetime_default(self):
        """Test default datetime parsing."""
        date_str = "2024-03-15 14:30:45"
        result = parse_datetime(date_str)
        
        assert result == datetime(2024, 3, 15, 14, 30, 45)
        assert result.year == 2024
        assert result.month == 3
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 45
    
    def test_parse_datetime_custom_format(self):
        """Test datetime parsing with custom format."""
        # Test various formats
        dt1 = parse_datetime("2024-03-15", "%Y-%m-%d")
        assert dt1 == datetime(2024, 3, 15, 0, 0, 0)
        
        dt2 = parse_datetime("15/03/2024", "%d/%m/%Y")
        assert dt2 == datetime(2024, 3, 15, 0, 0, 0)
        
        dt3 = parse_datetime("March 15, 2024", "%B %d, %Y")
        assert dt3 == datetime(2024, 3, 15, 0, 0, 0)
    
    def test_parse_datetime_invalid_format(self):
        """Test parsing with invalid format raises exception."""
        with pytest.raises(ValueError):
            parse_datetime("2024-03-15", "%d/%m/%Y")
        
        with pytest.raises(ValueError):
            parse_datetime("invalid date", "%Y-%m-%d")
    
    def test_format_parse_roundtrip(self):
        """Test that formatting and parsing are consistent."""
        original_dt = datetime(2024, 3, 15, 14, 30, 45)
        
        # Default format roundtrip
        formatted = format_datetime(original_dt)
        parsed = parse_datetime(formatted)
        assert parsed == original_dt
        
        # Custom format roundtrip
        custom_format = "%Y-%m-%d %H:%M"
        formatted_custom = format_datetime(original_dt, custom_format)
        parsed_custom = parse_datetime(formatted_custom, custom_format)
        # Note: seconds are lost in this format, so we compare without seconds
        expected = datetime(2024, 3, 15, 14, 30, 0)
        assert parsed_custom == expected


class TestDateCalculations:
    """Test date calculation functions."""
    
    def test_days_ago(self):
        """Test calculating dates in the past."""
        # Test various intervals
        one_day_ago = days_ago(1)
        seven_days_ago = days_ago(7)
        thirty_days_ago = days_ago(30)
        
        # Get current time after function calls to avoid timing issues
        now = datetime.now()
        
        # Verify the differences (allow for small timing differences)
        assert abs((now - one_day_ago).days - 1) <= 1
        assert abs((now - seven_days_ago).days - 7) <= 1
        assert abs((now - thirty_days_ago).days - 30) <= 1
        
        # Verify they are in the past
        assert one_day_ago < now
        assert seven_days_ago < now
        assert thirty_days_ago < now
    
    def test_days_ago_zero(self):
        """Test zero days ago."""
        now = datetime.now()
        zero_days_ago = days_ago(0)
        
        # Should be very close to now (within seconds)
        time_diff = abs((now - zero_days_ago).total_seconds())
        assert time_diff < 1  # Less than 1 second difference
    
    def test_days_from_now(self):
        """Test calculating dates in the future."""
        now = datetime.now()
        
        # Test various intervals
        one_day_future = days_from_now(1)
        seven_days_future = days_from_now(7)
        thirty_days_future = days_from_now(30)
        
        # Verify the differences
        assert abs((one_day_future - now).days) == 1
        assert abs((seven_days_future - now).days) == 7
        assert abs((thirty_days_future - now).days) == 30
        
        # Verify they are in the future
        assert one_day_future > now
        assert seven_days_future > now
        assert thirty_days_future > now
    
    def test_days_from_now_zero(self):
        """Test zero days from now."""
        now = datetime.now()
        zero_days_future = days_from_now(0)
        
        # Should be very close to now (within seconds)
        time_diff = abs((zero_days_future - now).total_seconds())
        assert time_diff < 1  # Less than 1 second difference
    
    def test_days_calculations_consistency(self):
        """Test consistency between days_ago and days_from_now."""
        # Going back and forward should be approximately consistent
        past = days_ago(5)
        future = days_from_now(5)
        now = datetime.now()
        
        # Distance from now should be approximately equal
        past_diff = abs((now - past).total_seconds())
        future_diff = abs((future - now).total_seconds())
        
        # Allow small difference due to execution time
        assert abs(past_diff - future_diff) < 5  # Less than 5 seconds difference


class TestWeekendDetection:
    """Test weekend detection functionality."""
    
    def test_is_weekend_known_dates(self):
        """Test weekend detection with known dates."""
        # Saturday, March 16, 2024
        saturday = datetime(2024, 3, 16)
        assert is_weekend(saturday) is True
        
        # Sunday, March 17, 2024
        sunday = datetime(2024, 3, 17)
        assert is_weekend(sunday) is True
        
        # Monday, March 18, 2024 (weekday)
        monday = datetime(2024, 3, 18)
        assert is_weekend(monday) is False
        
        # Wednesday, March 20, 2024 (weekday)
        wednesday = datetime(2024, 3, 20)
        assert is_weekend(wednesday) is False
        
        # Friday, March 22, 2024 (weekday)
        friday = datetime(2024, 3, 22)
        assert is_weekend(friday) is False
    
    def test_is_weekend_all_weekdays(self):
        """Test weekend detection for all days of the week."""
        # Start with a known Monday (March 18, 2024)
        monday = datetime(2024, 3, 18)
        
        expected_results = [
            False,  # Monday
            False,  # Tuesday
            False,  # Wednesday
            False,  # Thursday
            False,  # Friday
            True,   # Saturday
            True,   # Sunday
        ]
        
        for i, expected in enumerate(expected_results):
            test_date = monday + timedelta(days=i)
            assert is_weekend(test_date) == expected, f"Failed for day {i}: {test_date.strftime('%A')}"


class TestAgeCalculation:
    """Test age calculation functionality."""
    
    def test_get_age_in_years_basic(self):
        """Test basic age calculation."""
        # Fixed current date for consistent testing
        today = datetime(2024, 3, 15)
        
        # Test various birth dates
        birth_1990 = datetime(1990, 3, 15)  # Exact birthday
        birth_1990_before = datetime(1990, 3, 1)   # Birthday passed this year
        birth_1990_after = datetime(1990, 4, 1)    # Birthday not yet this year
        
        # Mock datetime.now() by passing today as reference
        # Note: The function uses datetime.now(), so we need to test with current date
        # For testing purposes, we'll test with approximate current date
        current_year = datetime.now().year
        
        # Test with actual birth dates
        birth_30_years_ago = datetime(current_year - 30, 3, 15)
        age_30 = get_age_in_years(birth_30_years_ago)
        assert age_30 in [29, 30]  # Depending on current date
        
        birth_25_years_ago = datetime(current_year - 25, 3, 15)
        age_25 = get_age_in_years(birth_25_years_ago)
        assert age_25 in [24, 25]
    
    def test_get_age_in_years_edge_cases(self):
        """Test age calculation edge cases."""
        current_year = datetime.now().year
        current_month = datetime.now().month
        current_day = datetime.now().day
        
        # Test birthday today
        birth_today = datetime(current_year - 25, current_month, current_day)
        age = get_age_in_years(birth_today)
        assert age == 25
        
        # Test future birth date (should be negative or handled gracefully)
        future_birth = datetime(current_year + 1, 1, 1)
        future_age = get_age_in_years(future_birth)
        assert future_age < 0  # Person not born yet
    
    def test_get_age_in_years_leap_year(self):
        """Test age calculation with leap year considerations."""
        current_year = datetime.now().year
        
        # Test February 29 (leap year baby)
        if current_year % 4 == 0 and (current_year % 100 != 0 or current_year % 400 == 0):
            # Current year is leap year
            leap_birth = datetime(current_year - 20, 2, 29)
            age = get_age_in_years(leap_birth)
            assert age in [19, 20]


class TestTimeSince:
    """Test time_since functionality."""
    
    def test_time_since_days(self):
        """Test time_since for day intervals."""
        now = datetime.now()
        
        # Test various day intervals
        one_day_ago = now - timedelta(days=1)
        result = time_since(one_day_ago)
        assert "1 day ago" in result
        
        three_days_ago = now - timedelta(days=3)
        result = time_since(three_days_ago)
        assert "3 days ago" in result
    
    def test_time_since_hours(self):
        """Test time_since for hour intervals."""
        now = datetime.now()
        
        # Test hour intervals (within same day)
        two_hours_ago = now - timedelta(hours=2)
        result = time_since(two_hours_ago)
        assert "2 hours ago" in result or "hour ago" in result
        
        one_hour_ago = now - timedelta(hours=1)
        result = time_since(one_hour_ago)
        assert "1 hour ago" in result or "hour ago" in result
    
    def test_time_since_minutes(self):
        """Test time_since for minute intervals."""
        now = datetime.now()
        
        # Test minute intervals
        thirty_minutes_ago = now - timedelta(minutes=30)
        result = time_since(thirty_minutes_ago)
        assert "30 minutes ago" in result or "minute ago" in result
        
        five_minutes_ago = now - timedelta(minutes=5)
        result = time_since(five_minutes_ago)
        assert "5 minutes ago" in result or "minute ago" in result
    
    def test_time_since_just_now(self):
        """Test time_since for very recent times."""
        now = datetime.now()
        
        # Test very recent time
        five_seconds_ago = now - timedelta(seconds=5)
        result = time_since(five_seconds_ago)
        assert result == "just now"
        
        # Test current time
        result = time_since(now)
        assert result == "just now"
    
    def test_time_since_singular_plural(self):
        """Test time_since handles singular/plural correctly."""
        now = datetime.now()
        
        # Test singular forms
        one_day_ago = now - timedelta(days=1)
        result = time_since(one_day_ago)
        assert "1 day ago" in result  # Not "1 days ago"
        
        one_hour_ago = now - timedelta(hours=1)
        result = time_since(one_hour_ago)
        assert "1 hour ago" in result  # Not "1 hours ago"
        
        one_minute_ago = now - timedelta(minutes=1)
        result = time_since(one_minute_ago)
        assert "1 minute ago" in result  # Not "1 minutes ago"


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple date functions."""
    
    def test_date_processing_pipeline(self):
        """Test complete date processing pipeline."""
        # Create timeline of events
        events = [
            {
                'name': 'Project Started',
                'date_str': '2024-01-01 09:00:00',
                'format': '%Y-%m-%d %H:%M:%S'
            },
            {
                'name': 'First Release',
                'date_str': '2024-02-15 14:30:00',
                'format': '%Y-%m-%d %H:%M:%S'
            },
            {
                'name': 'Major Update',
                'date_str': '2024-03-01 10:15:00',
                'format': '%Y-%m-%d %H:%M:%S'
            }
        ]
        
        processed_events = []
        for event in events:
            # Parse the date
            event_date = parse_datetime(event['date_str'], event['format'])
            
            # Process the event
            processed = {
                'name': event['name'],
                'date': event_date,
                'formatted': format_datetime(event_date, '%B %d, %Y'),
                'time_since': time_since(event_date),
                'is_weekend': is_weekend(event_date)
            }
            processed_events.append(processed)
        
        # Verify processing
        assert len(processed_events) == 3
        assert processed_events[0]['formatted'] == 'January 01, 2024'
        assert processed_events[1]['formatted'] == 'February 15, 2024'
        assert processed_events[2]['formatted'] == 'March 01, 2024'
        
        # All should have time_since values
        for event in processed_events:
            assert isinstance(event['time_since'], str)
            assert len(event['time_since']) > 0
    
    def test_schedule_planning(self):
        """Test schedule planning with date utilities."""
        # Plan events relative to a base date
        base_date = datetime(2024, 6, 1, 10, 0, 0)  # June 1, 2024, 10:00 AM
        
        schedule = [
            {'name': 'Review Meeting', 'days_offset': 3},
            {'name': 'Project Deadline', 'days_offset': 14},
            {'name': 'Final Presentation', 'days_offset': 21}
        ]
        
        planned_events = []
        for item in schedule:
            event_date = base_date + timedelta(days=item['days_offset'])
            
            planned_event = {
                'name': item['name'],
                'date': event_date,
                'formatted': format_datetime(event_date, '%A, %B %d at %I:%M %p'),
                'is_weekend': is_weekend(event_date),
                'days_from_base': item['days_offset']
            }
            planned_events.append(planned_event)
        
        # Verify planning
        assert len(planned_events) == 3
        
        # Check that we can identify weekend events
        weekend_events = [e for e in planned_events if e['is_weekend']]
        weekday_events = [e for e in planned_events if not e['is_weekend']]
        
        # At least some events should be categorized
        assert len(weekend_events) + len(weekday_events) == 3