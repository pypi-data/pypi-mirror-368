from datetime import datetime, date, timezone, timedelta
import pytz
import re

class QuanticTime:
    def __init__(self, value):
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            self._timestamp = int(value.astimezone(timezone.utc).timestamp())
        elif isinstance(value, date):
            dt = datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
            self._timestamp = int(dt.timestamp())
        elif isinstance(value, (int, float)):
            self._timestamp = int(value)
        elif isinstance(value, str):
            # Auto-parse common string formats
            self._timestamp = self._parse_string(value)
        else:
            raise TypeError("Value must be datetime, date, string, or unix timestamp")

    @classmethod
    def from_string(cls, date_string, fmt=None, tz="UTC"):
        """
        Create QuanticTime instance from string with specified format.

        Args:
            date_string (str): The date string to parse
            fmt (str, optional): Format string. If None, auto-detect common formats
            tz (str): Timezone for the input string (default: UTC)

        Returns:
            QuanticTime: New instance
        """
        if fmt is None:
            return cls(date_string)

        try:
            tz_obj = pytz.timezone(tz)
            dt = datetime.strptime(date_string, fmt)
            if dt.tzinfo is None:
                dt = tz_obj.localize(dt)
            return cls(dt)
        except ValueError as e:
            raise ValueError(f"Unable to parse '{date_string}' with format '{fmt}': {e}")

    @classmethod
    def now(cls, tz="UTC"):
        """Create QuanticTime instance for current time."""
        tz_obj = pytz.timezone(tz)
        return cls(datetime.now(tz_obj))

    @classmethod
    def today(cls, tz="UTC"):
        """Create QuanticTime instance for today at midnight."""
        tz_obj = pytz.timezone(tz)
        today = datetime.now(tz_obj).date()
        return cls(today)

    @staticmethod
    def list_timezones(filter_text=None, limit=None, show_common_only=False):
        """
        List available timezones with optional filtering.

        Args:
            filter_text (str, optional): Filter timezones containing this text (case-insensitive)
            limit (int, optional): Maximum number of timezones to return
            show_common_only (bool): If True, show only common timezones

        Returns:
            list: List of timezone names
        """
        if show_common_only:
            # Common timezones that are frequently used
            timezones = [
                'UTC',
                'Chile/Continental',
                'Chile/EasterIsland',
                'America/Santiago',
                'America/Punta_Arenas',
                'America/Mexico_City',
                'America/Buenos_Aires',
                'America/Lima',
                'US/Eastern',
                'US/Central',
                'US/Mountain',
                'US/Pacific',
                'Europe/London',
                'Europe/Paris',
                'Europe/Berlin',
                'Europe/Madrid',
                'Europe/Rome',
                'Asia/Tokyo',
                'Asia/Shanghai',
                'Asia/Dubai',
                'Australia/Sydney',
                'Australia/Melbourne',
                'America/New_York',
                'America/Denver',
                'America/Los_Angeles',
            ]
        else:
            timezones = pytz.all_timezones

        # Apply filter if provided
        if filter_text:
            filter_lower = filter_text.lower()
            timezones = [tz for tz in timezones if filter_lower in tz.lower()]

        # Sort alphabetically
        timezones = sorted(timezones)

        # Apply limit if provided
        if limit:
            timezones = timezones[:limit]

        return list(timezones)

    @staticmethod
    def search_timezones(search_term, limit=20):
        """
        Search for timezones containing the search term.

        Args:
            search_term (str): Term to search for in timezone names
            limit (int): Maximum number of results to return (default: 20)

        Returns:
            list: List of matching timezone names with additional info
        """
        search_lower = search_term.lower()
        matches = []

        for tz_name in pytz.all_timezones:
            if search_lower in tz_name.lower():
                try:
                    tz = pytz.timezone(tz_name)
                    now = datetime.now(tz)
                    offset = now.strftime('%z')
                    # Format offset nicely (e.g., +0500 -> +05:00)
                    if len(offset) == 5:
                        offset = offset[:3] + ':' + offset[3:]

                    matches.append({
                        'timezone': tz_name,
                        'offset': offset,
                        'abbreviation': now.strftime('%Z'),
                        'current_time': now.strftime('%Y-%m-%d %H:%M:%S')
                    })
                except:
                    # Some timezones might have issues, skip them
                    continue

        # Sort by timezone name
        matches.sort(key=lambda x: x['timezone'])

        return matches[:limit] if limit else matches

    @staticmethod
    def print_timezones(filter_text=None, limit=50, show_common_only=False, detailed=False):
        """
        Print available timezones in a user-friendly format.

        Args:
            filter_text (str, optional): Filter timezones containing this text
            limit (int): Maximum number of timezones to display (default: 50)
            show_common_only (bool): If True, show only common timezones
            detailed (bool): If True, show additional info like current time and offset
        """
        if detailed:
            # For detailed view, we need to create the detailed info regardless of filter
            if filter_text:
                # Use search function for detailed info with filter
                matches = QuanticTime.search_timezones(filter_text, limit)
                title = f"Found {len(matches)} timezone(s) matching '{filter_text}'"
            else:
                # Get timezone names and create detailed info
                timezone_names = QuanticTime.list_timezones(show_common_only=show_common_only)
                if limit:
                    timezone_names = timezone_names[:limit]

                matches = []
                for tz_name in timezone_names:
                    try:
                        tz = pytz.timezone(tz_name)
                        now = datetime.now(tz)
                        offset = now.strftime('%z')
                        # Format offset nicely (e.g., +0500 -> +05:00)
                        if len(offset) == 5:
                            offset = offset[:3] + ':' + offset[3:]

                        matches.append({
                            'timezone': tz_name,
                            'offset': offset,
                            'abbreviation': now.strftime('%Z'),
                            'current_time': now.strftime('%Y-%m-%d %H:%M:%S')
                        })
                    except:
                        # Some timezones might have issues, skip them
                        continue

                type_label = "common" if show_common_only else "all"
                title = f"Showing detailed info for {type_label} timezones"

            if not matches:
                search_info = f" matching '{filter_text}'" if filter_text else ""
                print(f"No timezones found{search_info}")
                return

            print(f"\n{title}:")
            print("-" * 80)
            print(f"{'Timezone':<35} {'Offset':<8} {'Abbr':<6} {'Current Time'}")
            print("-" * 80)

            for match in matches:
                print(f"{match['timezone']:<35} {match['offset']:<8} {match['abbreviation']:<6} {match['current_time']}")

        else:
            # Simple list
            timezones = QuanticTime.list_timezones(filter_text, limit, show_common_only)

            if not timezones:
                print(f"No timezones found matching '{filter_text}'")
                return

            type_label = "common" if show_common_only else "all"
            filter_label = f" matching '{filter_text}'" if filter_text else ""

            print(f"\nShowing {len(timezones)} {type_label} timezone(s){filter_label}:")
            print("-" * 50)

            # Print in columns for better readability
            for i, tz in enumerate(timezones, 1):
                print(f"{i:3d}. {tz}")
                if i % 25 == 0 and i < len(timezones):
                    input("Press Enter to continue...")  # Pagination for long lists

    def _parse_string(self, date_string):
        """Parse common date string formats automatically."""
        # Remove any timezone info for now (basic implementation)
        clean_string = re.sub(r'\s*\([^)]*\)$', '', date_string.strip())

        # Common formats to try
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%m/%d/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%d/%m/%Y %H:%M:%S",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(clean_string, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return int(dt.timestamp())
            except ValueError:
                continue

        raise ValueError(f"Unable to parse date string: '{date_string}'")

    @property
    def timestamp(self):
        return self._timestamp

    def to_datetime(self, tz="UTC"):
        tz_obj = pytz.timezone(tz)
        return datetime.fromtimestamp(self._timestamp, tz_obj)

    def to_string(self, fmt="%Y-%m-%d %H:%M:%S", tz="UTC"):
        return self.to_datetime(tz).strftime(fmt)

    def to_iso(self, tz="UTC"):
        """Return ISO 8601 formatted string."""
        return self.to_datetime(tz).isoformat()

    def add_seconds(self, seconds):
        """Add seconds and return new QuanticTime instance."""
        return QuanticTime(self._timestamp + seconds)

    def add_minutes(self, minutes):
        """Add minutes and return new QuanticTime instance."""
        return self.add_seconds(minutes * 60)

    def add_hours(self, hours):
        """Add hours and return new QuanticTime instance."""
        return self.add_seconds(hours * 3600)

    def add_days(self, days):
        """Add days and return new QuanticTime instance."""
        return self.add_seconds(days * 86400)

    def difference(self, other):
        """
        Calculate difference in seconds between two QuanticTime instances.
        Returns positive if self is later than other.
        """
        if not isinstance(other, QuanticTime):
            raise TypeError("Can only calculate difference with another QuanticTime")
        return self._timestamp - other._timestamp

    def is_weekend(self, tz="UTC"):
        """Check if the date falls on a weekend."""
        dt = self.to_datetime(tz)
        return dt.weekday() >= 5  # 5=Saturday, 6=Sunday

    def start_of_day(self, tz="UTC"):
        """Get QuanticTime for start of the day (midnight)."""
        dt = self.to_datetime(tz)
        start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return QuanticTime(start)

    def end_of_day(self, tz="UTC"):
        """Get QuanticTime for end of the day (23:59:59)."""
        dt = self.to_datetime(tz)
        end = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        return QuanticTime(end)

    def __repr__(self):
        return f"<QuanticTime {self.to_string()} UTC>"

    def __str__(self):
        return self.to_string()

    def __eq__(self, other):
        return isinstance(other, QuanticTime) and self._timestamp == other._timestamp

    def __lt__(self, other):
        if not isinstance(other, QuanticTime):
            raise TypeError("Can only compare with another QuanticTime")
        return self._timestamp < other._timestamp

    def __le__(self, other):
        if not isinstance(other, QuanticTime):
            raise TypeError("Can only compare with another QuanticTime")
        return self._timestamp <= other._timestamp

    def __gt__(self, other):
        if not isinstance(other, QuanticTime):
            raise TypeError("Can only compare with another QuanticTime")
        return self._timestamp > other._timestamp

    def __ge__(self, other):
        if not isinstance(other, QuanticTime):
            raise TypeError("Can only compare with another QuanticTime")
        return self._timestamp >= other._timestamp

    def __add__(self, other):
        """Add seconds (int/float) or timedelta to QuanticTime."""
        if isinstance(other, (int, float)):
            return QuanticTime(self._timestamp + other)
        elif isinstance(other, timedelta):
            return QuanticTime(self._timestamp + int(other.total_seconds()))
        else:
            raise TypeError("Can only add int, float, or timedelta")

    def __sub__(self, other):
        """Subtract seconds (int/float), timedelta, or another QuanticTime."""
        if isinstance(other, (int, float)):
            return QuanticTime(self._timestamp - other)
        elif isinstance(other, timedelta):
            return QuanticTime(self._timestamp - int(other.total_seconds()))
        elif isinstance(other, QuanticTime):
            return self._timestamp - other._timestamp  # Return difference in seconds
        else:
            raise TypeError("Can only subtract int, float, timedelta, or QuanticTime")

    def __hash__(self):
        return hash(self._timestamp)


if __name__ == "__main__":
    QuanticTime.print_timezones(show_common_only=True, detailed=True)