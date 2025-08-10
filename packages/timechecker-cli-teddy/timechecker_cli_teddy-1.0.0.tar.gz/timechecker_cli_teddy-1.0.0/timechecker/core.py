"""Core timezone functionality."""

import logging
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

class TimeChecker:
    """Main class for timezone operations."""
    
    SUPPORTED_TIMEZONES = {
        'PST': 'US/Pacific',
        'EST': 'US/Eastern', 
        'BST': 'Europe/London',
        'WAT': 'Africa/Lagos',
        'CET': 'Europe/Berlin'
    }
    
    def __init__(self):
        logger.debug("TimeChecker initialized")
    
    def get_time(self, timezone_code: str) -> str:
        """Get current time for specified timezone code."""
        if timezone_code not in self.SUPPORTED_TIMEZONES:
            raise ValueError(f"Unsupported timezone: {timezone_code}")
        
        tz_name = self.SUPPORTED_TIMEZONES[timezone_code]
        tz = pytz.timezone(tz_name)
        current_time = datetime.now(tz)
        
        logger.info(f"Retrieved time for {timezone_code}: {current_time}")
        return current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    
    def list_timezones(self) -> list:
        """List all supported timezone codes."""
        return list(self.SUPPORTED_TIMEZONES.keys())

def get_timezone_time(timezone_code: str) -> str:
    """Convenience function to get timezone time."""
    checker = TimeChecker()
    return checker.get_time(timezone_code)