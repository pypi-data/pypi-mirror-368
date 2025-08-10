#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime
import pytz

TIMEZONES = {
    'PST': 'US/Pacific',
    'EST': 'US/Eastern', 
    'BST': 'Europe/London',
    'CET': 'Europe/Berlin',
    'WAT': 'Africa/Lagos'
}

def get_time_in_timezone(tz_code):
    if tz_code not in TIMEZONES:
        return None
    
    tz = pytz.timezone(TIMEZONES[tz_code])
    now = datetime.now(tz)
    return now.strftime('%Y-%m-%d %H:%M:%S %Z')

def main():
    parser = argparse.ArgumentParser(description='Get current time in different timezones')
    parser.add_argument('-p', '--timezone', required=True, 
                       choices=list(TIMEZONES.keys()),
                       help='Timezone code (PST, EST, BST, CET, WAT)')
    
    args = parser.parse_args()
    
    time_str = get_time_in_timezone(args.timezone)
    if time_str:
        print(f"{args.timezone}: {time_str}")
    else:
        print(f"Error: Unknown timezone {args.timezone}")
        sys.exit(1)

if __name__ == '__main__':
    main()