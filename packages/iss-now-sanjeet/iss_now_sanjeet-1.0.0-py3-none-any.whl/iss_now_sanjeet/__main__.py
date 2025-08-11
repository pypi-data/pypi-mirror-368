# iss_pass_tracker/__main__.py
import argparse
from . import get_current_location

def main():
    parser = argparse.ArgumentParser(description="ISS Tracker CLI")
    parser.add_argument(
        "--now", 
        action="store_true", 
        help="Show current ISS location"
    )
    args = parser.parse_args()

    if args.now:
        lat, lon, ts = get_current_location()
        print(f"ISS is currently at {lat:.4f}°, {lon:.4f}° at {ts.isoformat()}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
