def main():
#!/usr/bin/env python3
import sys
import urllib.request
import json
import ssl
import certifi
from urllib.parse import quote
from datetime import datetime, timezone, timedelta
import time

# Terminal colors and styles
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'

def print_banner():
    """Print a stylish banner."""
    banner = f"""
{Colors.OKCYAN}╔══════════════════════════════════════════════════════════╗
║                    🌍 WORLD TIME CLI 🕐                  ║
╚══════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)

def print_loading(message):
    """Print loading message with animation."""
    print(f"{Colors.DIM}⏳ {message}...{Colors.ENDC}")

def print_success(message):
    """Print success message."""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    """Print error message."""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def print_warning(message):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_time_result(place, location_name, time_str, timezone_str, is_approximation=False):
    """Print the final time result with fancy formatting."""
    
    # Convert to 12-hour format if it's in 24-hour format
    try:
        if ":" in time_str and len(time_str.split(":")) >= 2:
            hour, minute = time_str.split(":")[:2]
            second = time_str.split(":")[2] if len(time_str.split(":")) > 2 else "00"
            
            hour_24 = int(hour)
            am_pm = "AM" if hour_24 < 12 else "PM"
            hour_12 = hour_24 % 12
            if hour_12 == 0:
                hour_12 = 12
            
            time_12_format = f"{hour_12:02d}:{minute}:{second} {am_pm}"
        else:
            time_12_format = time_str
    except:
        time_12_format = time_str

    # Create the result box
    result = f"""
{Colors.OKBLUE}╭─────────────────────────────────────────────────────────────╮{Colors.ENDC}
{Colors.OKBLUE}│{Colors.ENDC}  {Colors.BOLD}📍 Location:{Colors.ENDC} {location_name[:45]}{'...' if len(location_name) > 45 else '':<8} {Colors.OKBLUE}│{Colors.ENDC}
{Colors.OKBLUE}│{Colors.ENDC}                                                             {Colors.OKBLUE}│{Colors.ENDC}
{Colors.OKBLUE}│{Colors.ENDC}  {Colors.BOLD}🕐 Current Time:{Colors.ENDC}                                        {Colors.OKBLUE}│{Colors.ENDC}
{Colors.OKBLUE}│{Colors.ENDC}     {Colors.OKGREEN}{Colors.BOLD}{time_12_format:^15}{Colors.ENDC}                               {Colors.OKBLUE}│{Colors.ENDC}
{Colors.OKBLUE}│{Colors.ENDC}                                                             {Colors.OKBLUE}│{Colors.ENDC}
{Colors.OKBLUE}│{Colors.ENDC}  {Colors.BOLD}🌐 Timezone:{Colors.ENDC} {Colors.OKCYAN}{timezone_str}{Colors.ENDC}                                   {Colors.OKBLUE}│{Colors.ENDC}"""

    if is_approximation:
        result += f"""
{Colors.OKBLUE}│{Colors.ENDC}  {Colors.WARNING}⚠️  Approximate time (API unavailable){Colors.ENDC}               {Colors.OKBLUE}│{Colors.ENDC}"""
    
    result += f"""
{Colors.OKBLUE}╰─────────────────────────────────────────────────────────────╯{Colors.ENDC}
"""
    
    print(result)

def print_separator():
    """Print a separator line."""
    print(f"{Colors.DIM}{'─' * 60}{Colors.ENDC}")

# Use certifi's certificates instead of system ones
ssl_context = ssl.create_default_context(cafile=certifi.where())

def get_location_info(place):
    """Get latitude, longitude, and timezone for a place name."""
    try:
        # Using Nominatim API to get coordinates
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={quote(place)}&limit=1"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'TimeCLI/1.0')
        
        with urllib.request.urlopen(req, context=ssl_context) as response:
            data = json.load(response)
        
        if not data:
            print_error(f"No results found for: {place}")
            return None
            
        return {
            "lat": float(data[0]["lat"]),
            "lon": float(data[0]["lon"]),
            "display_name": data[0]["display_name"]
        }
    except Exception as e:
        print_error(f"Error finding location: {e}")
        return None

def get_timezone_info(lat, lon):
    """Get timezone information for given coordinates."""
    try:
        # First try TimeAPI.io (free, no key required)
        url = f"https://timeapi.io/api/time/current/coordinate?latitude={lat}&longitude={lon}"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'TimeCLI/1.0')
        
        with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
            data = json.load(response)
        
        if data.get("timeZone"):
            return {
                "time": data.get("currentLocalTime", "").split("T")[1][:8] if data.get("currentLocalTime") else "",
                "timezone": data.get("timeZone", "Unknown"),
                "offset": 0,
                "is_approximation": False
            }
    except Exception as e:
        print_warning(f"Primary API unavailable")
    
    try:
        # Fallback to TimeZoneDB API
        url = f"http://api.timezonedb.com/v2.1/get-time-zone?key=KW0ZEYFBWBYZ&format=json&by=position&lat={lat}&lng={lon}"
        
        with urllib.request.urlopen(url, context=ssl_context, timeout=10) as response:
            data = json.load(response)
        
        if data.get("status") == "OK":
            return {
                "time": data.get("formatted", "").split(" ")[1] if data.get("formatted") else "",
                "timezone": data.get("zoneName", "Unknown"),
                "offset": data.get("gmtOffset", 0) / 3600,
                "is_approximation": False
            }
    except Exception as e:
        print_warning(f"Secondary API unavailable")
    
    # If both APIs fail, return None to trigger approximation
    return None

def get_time_worldtimeapi(lat, lon):
    """Fallback method using WorldTimeAPI."""
    try:
        # Round coordinates to avoid too precise queries
        lat = round(lat, 2)
        lon = round(lon, 2)
        
        # Try to get timezone by coordinates (this might not work for all locations)
        # So we'll use a different approach - get timezone by IP location as fallback
        url = "http://worldtimeapi.org/api/ip"
        
        with urllib.request.urlopen(url, context=ssl_context) as response:
            data = json.load(response)
            
        return {
            "time": data.get("datetime", "").split("T")[1].split(".")[0] if data.get("datetime") else "",
            "timezone": data.get("timezone", "Unknown"),
            "offset": data.get("raw_offset", 0)
        }
    except Exception as e:
        print(f"Error with fallback API: {e}")
        return None

def get_simple_time_estimate(lat, lon):
    """Calculate approximate time based on longitude offset."""
    try:
        # Simple calculation: each 15 degrees of longitude ≈ 1 hour
        utc_now = datetime.now(timezone.utc)
        hours_offset = lon / 15.0
        
        # Create timezone offset
        tz_offset = timedelta(hours=hours_offset)
        local_tz = timezone(tz_offset)
        
        # Get local time
        local_time = utc_now.astimezone(local_tz)
        
        return {
            "time": local_time.strftime("%H:%M:%S"),
            "timezone": f"UTC{hours_offset:+.1f}",
            "offset": hours_offset,
            "is_approximation": True
        }
    except Exception as e:
        print_error(f"Error calculating time: {e}")
        return None

def main():
    print_banner()
    
    if len(sys.argv) < 2:
        print(f"{Colors.WARNING}Usage:{Colors.ENDC}")
        print(f"  {Colors.BOLD}python3 timecli.py <place name>{Colors.ENDC}")
        print(f"  {Colors.BOLD}python3 timecli.py -<place name>{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}Examples:{Colors.ENDC}")
        print(f"  {Colors.DIM}python3 timecli.py Tokyo{Colors.ENDC}")
        print(f"  {Colors.DIM}python3 timecli.py -\"New York\"{Colors.ENDC}")
        print(f"  {Colors.DIM}python3 timecli.py London{Colors.ENDC}")
        print()
        sys.exit(1)
    
    # Handle both "place" and "-place" formats
    place = " ".join(sys.argv[1:]).lstrip("-").strip()
    
    if not place:
        print_error("Please provide a place name")
        sys.exit(1)
    
    print_loading(f"Searching for location: {Colors.BOLD}{place}{Colors.ENDC}")
    
    # Get location coordinates
    location_info = get_location_info(place)
    if not location_info:
        sys.exit(1)
    
    print_success(f"Found: {location_info['display_name']}")
    print_separator()
    
    print_loading("Fetching current time")
    
    # Try to get accurate time from APIs
    time_info = get_timezone_info(location_info["lat"], location_info["lon"])
    
    if not time_info or not time_info.get("time"):
        print_warning("Using geographical approximation")
        time_info = get_simple_time_estimate(location_info["lat"], location_info["lon"])
    
    if not time_info:
        print_error("Unable to determine time for this location")
        sys.exit(1)
    
    # Display results with fancy formatting
    print_time_result(
        place,
        location_info['display_name'],
        time_info['time'],
        time_info['timezone'],
        time_info.get('is_approximation', False)
    )

if __name__ == "__main__":
    main()