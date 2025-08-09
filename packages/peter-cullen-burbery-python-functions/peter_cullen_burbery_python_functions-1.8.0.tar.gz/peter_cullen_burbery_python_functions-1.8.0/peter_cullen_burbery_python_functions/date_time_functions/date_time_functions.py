"""
Date/time utility functions for high-precision local timestamps.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
import tzlocal
import time

def date_time_stamp() -> str:
    """
    Returns a high-precision local timestamp string including:

    - Gregorian calendar date
    - Local time with nanosecond precision
    - IANA time zone
    - ISO week format: YYYY-Www-ddd
    - Ordinal day of the year

    Format:
        'YYYY-MMM-DDD HHH.MMM.SSS.NNNNNNNNN TZ_NAME YYYY-Www-ddd YYYY-DDD'

    Example:
        >>> date_time_stamp()
        '2025-007-030 016.035.051.123456789 America/New_York 2025-W031-003 2025-211'

    Returns:
        str: Formatted timestamp string with nanosecond precision and multiple calendar representations.
    """
    # Get local timezone and nanoseconds since epoch
    local_timezone: ZoneInfo = tzlocal.get_localzone()
    ns_since_epoch: int = time.time_ns()

    # Convert nanoseconds to seconds
    seconds_since_epoch: float = ns_since_epoch / 1_000_000_000
    now: datetime = datetime.fromtimestamp(seconds_since_epoch, tz=ZoneInfo(local_timezone.key))

    # Extract nanosecond portion
    nanosecond_part: int = ns_since_epoch % 1_000_000_000

    # Format date/time components
    date_part: str = f"{now.year}-{now.month:03d}-{now.day:03d}"  # YYYY-MMM-DDD
    time_part: str = f"{now.hour:03d}.{now.minute:03d}.{now.second:03d}.{nanosecond_part:09d}"  # HHH.MMM.SSS.NNNNNNNNN
    time_zone: str = local_timezone.key

    # ISO week
    iso_year, iso_week, iso_weekday = now.isocalendar()
    iso_week_str: str = f"{iso_week:03d}"
    iso_weekday_str: str = f"{iso_weekday:03d}"
    # ISO ordinal date
    day_of_year: str = f"{now.timetuple().tm_yday:03d}"
    gregorian_year: str = str(now.year)

    return (
        f"{date_part} {time_part} {time_zone} "
        f"{iso_year:04d}-W{iso_week_str}-{iso_weekday_str} {gregorian_year}-{day_of_year}"
    )

def generate_pdb_name_from_timestamp() -> str:
    """
    Generates a dynamic PDB name in the format:
    pdb_<YYYY>_<MMM>_<DDD>_<HHH>_<MMM>_<SSS>

    Example:
        pdb_2025_007_031_017_020_008

    Returns:
        str: Dynamically constructed PDB name based on the current local time.
    """
    # Get the local time zone using tzlocal and zoneinfo
    local_tz: ZoneInfo = tzlocal.get_localzone()
    
    # Get the current local datetime with time zone awareness
    now: datetime = datetime.now(ZoneInfo(local_tz.key))

    # Extract and format each datetime component as 3-digit strings (except year)
    year: str = f"{now.year}"        # e.g. "2025"
    month: str = f"{now.month:03d}"  # e.g. "007" for July
    day: str = f"{now.day:03d}"      # e.g. "031" for the 31st
    hour: str = f"{now.hour:03d}"    # e.g. "017" for 5 PM
    minute: str = f"{now.minute:03d}"# e.g. "020"
    second: str = f"{now.second:03d}"# e.g. "008"

    # Assemble the PDB name string
    return f"pdb_{year}_{month}_{day}_{hour}_{minute}_{second}"

def generate_prefixed_timestamp(prefix: str) -> str:
    """
    Generates a high-precision, time zone-aware timestamp string with a given prefix.

    The format returned is:
        <prefix>_YYYY_MMM_DDD_HHH_MMM_SSS_NNNNNNNNN_TimeZone_ISOYEAR_WWWW_WEEKDAY_YYYY_DOY

    Example:
        big_data_test_2025_007_031_019_007_040_353635000_America_slash_New_York_2025_W031_004_2025_212

    Args:
        prefix (str): A string prefix such as "big_data_test" or "everyday_calculations".

    Returns:
        str: A formatted timestamp string with the given prefix.
    """
    local_timezone: ZoneInfo = tzlocal.get_localzone()
    ns_since_epoch: int = time.time_ns()
    seconds_since_epoch: float = ns_since_epoch / 1_000_000_000
    now: datetime = datetime.fromtimestamp(seconds_since_epoch, tz=ZoneInfo(local_timezone.key))
    nanosecond_part: int = ns_since_epoch % 1_000_000_000

    # Main components
    year: str = f"{now.year}"
    month: str = f"{now.month:03d}"
    day: str = f"{now.day:03d}"
    hour: str = f"{now.hour:03d}"
    minute: str = f"{now.minute:03d}"
    second: str = f"{now.second:03d}"
    nanoseconds: str = f"{nanosecond_part:09d}"
    time_zone: str = local_timezone.key.replace("/", "_slash_")

    # ISO week info
    iso_year, iso_week, iso_weekday = now.isocalendar()
    iso_week_str: str = f"{iso_week:03d}"
    iso_weekday_str: str = f"{iso_weekday:03d}"
    day_of_year: str = f"{now.timetuple().tm_yday:03d}"

    return (
        f"{prefix}_{year}_{month}_{day}_{hour}_{minute}_{second}_"
        f"{nanoseconds}_{time_zone}_{iso_year:04d}_W{iso_week_str}_{iso_weekday_str}_"
        f"{year}_{day_of_year}"
    )

def get_timestamp() -> str:
    """
    Returns a high-precision, time zone-aware timestamp string:
    YYYY_MMM_DDD_HHH_MMM_SSS_NNNNNNNNN_TimeZone_ISOYEAR_WWWW_WEEKDAY_YYYY_DOY_UnixSeconds_Nanoseconds

    Example:
        2025_008_004_013_048_029_083107000_America_slash_New_York_2025_W032_001_2025_216_1754681668_083107000
    """
    # Local TZ and now with nanoseconds
    local_tz: ZoneInfo = tzlocal.get_localzone()
    ns_since_epoch: int = time.time_ns()
    seconds_since_epoch: int = ns_since_epoch // 1_000_000_000  # integer seconds
    nanos_part: int = ns_since_epoch % 1_000_000_000
    now: datetime = datetime.fromtimestamp(seconds_since_epoch, tz=ZoneInfo(local_tz.key))

    # Components
    year: str = f"{now.year}"
    month: str = f"{now.month:03d}"
    day: str = f"{now.day:03d}"
    hour: str = f"{now.hour:03d}"
    minute: str = f"{now.minute:03d}"
    second: str = f"{now.second:03d}"
    nanoseconds: str = f"{nanos_part:09d}"
    time_zone: str = local_tz.key.replace("/", "_slash_")

    # ISO week info and ordinal day
    iso_year, iso_week, iso_weekday = now.isocalendar()
    iso_week_str: str = f"{iso_week:03d}"
    iso_weekday_str: str = f"{iso_weekday:03d}"
    day_of_year: str = f"{now.timetuple().tm_yday:03d}"

    return (
        f"{year}_{month}_{day}_{hour}_{minute}_{second}_"
        f"{nanoseconds}_{time_zone}_{iso_year:04d}_W{iso_week_str}_{iso_weekday_str}_"
        f"{year}_{day_of_year}_{seconds_since_epoch}_{nanoseconds}"
    )