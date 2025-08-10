import argparse
import sys
from . import get_time_in_timezone, get_all_times, TIMEZONE_MAP

def main():
    parser = argparse.ArgumentParser(description='Get current time in different timezones')
    parser.add_argument('--timezone', '-t', choices=list(TIMEZONE_MAP.keys()), 
                       help='Specific timezone to query')
    parser.add_argument('--all', '-a', action='store_true', 
                       help='Show all supported timezones')
    
    args = parser.parse_args()
    
    if args.all:
        times = get_all_times()
        for tz, time in times.items():
            print(f"{tz}: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    elif args.timezone:
        time = get_time_in_timezone(args.timezone)
        print(f"{args.timezone}: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    else:
        print("Available timezones:", ", ".join(TIMEZONE_MAP.keys()))
        print("Use --all to see all times or --timezone <TZ> for specific timezone")

if __name__ == '__main__':
    main()