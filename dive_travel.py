from datetime import datetime, timedelta
from typing import Tuple, Optional

class DiveTravelCalculator:
    def __init__(self):
        # Define recommended surface intervals (in hours) for each organization
        self.surface_intervals = {
            'DAN': {
                'single': 12,
                'multiple': 18
            },
            'PADI': {
                'single': 12,
                'multiple': 18
            },
            'NAUI': {
                'single': 24,
                'multiple': 24
            }
        }

    def get_required_interval(self, organization: str, multiple_dives: bool) -> int:
        """Get required surface interval in hours before flying."""
        if organization not in self.surface_intervals:
            raise ValueError(f"Unknown organization: {organization}")
        
        dive_type = 'multiple' if multiple_dives else 'single'
        return self.surface_intervals[organization][dive_type]

    def is_safe_to_fly(self, last_dive_time: datetime, flight_time: datetime, 
                       organization: str, multiple_dives: bool) -> Tuple[bool, str]:
        """
        Check if it's safe to fly based on the last dive and organization guidelines.
        Returns (is_safe, message)
        """
        required_hours = self.get_required_interval(organization, multiple_dives)
        time_diff = flight_time - last_dive_time
        hours_until_flight = time_diff.total_seconds() / 3600

        if hours_until_flight < 0:
            return False, "Error: Flight time is before dive time!"

        if hours_until_flight >= required_hours:
            return True, f"✅ Safe to fly! You'll have {hours_until_flight:.1f} hours of surface interval (minimum required: {required_hours} hours)"
        else:
            hours_short = required_hours - hours_until_flight
            return False, f"⚠️ NOT safe to fly! You need {hours_short:.1f} more hours of surface interval"

def get_datetime_input(prompt: str) -> Optional[datetime]:
    """Get and validate datetime input from user."""
    while True:
        try:
            date_str = input(prompt + " (format: YYYY-MM-DD HH:MM): ")
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD HH:MM (e.g., 2025-03-26 14:30)")
        except KeyboardInterrupt:
            return None

def main():
    print("\n=== Dive Travel Safety Calculator ===\n")
    print("This calculator helps determine if it's safe to fly after diving based on")
    print("recommended surface intervals from major diving organizations.\n")
    
    # Create calculator instance
    calculator = DiveTravelCalculator()
    
    # Get organization preference
    print("Which organization's guidelines do you follow?")
    print("1. DAN (Divers Alert Network)")
    print("2. PADI (Professional Association of Diving Instructors)")
    print("3. NAUI (National Association of Underwater Instructors)")
    
    while True:
        org_choice = input("\nEnter number (1-3): ").strip()
        if org_choice == "1":
            organization = "DAN"
            break
        elif org_choice == "2":
            organization = "PADI"
            break
        elif org_choice == "3":
            organization = "NAUI"
            break
        print("Invalid choice. Please enter 1, 2, or 3.")

    # Get dive history
    multiple_dives = input("\nDid you do multiple dives? (yes/no): ").lower().startswith('y')
    
    # Get last dive time
    last_dive = get_datetime_input("\nWhen was your last dive")
    if not last_dive:
        print("\nCalculation cancelled.")
        return

    # Get flight time
    flight_time = get_datetime_input("\nWhen is your flight")
    if not flight_time:
        print("\nCalculation cancelled.")
        return

    # Check if safe to fly
    is_safe, message = calculator.is_safe_to_fly(last_dive, flight_time, organization, multiple_dives)
    
    print("\n" + "=" * 50)
    print(message)
    
    if not is_safe:
        print("\n⚠️ WARNING: Flying too soon after diving increases your risk of")
        print("decompression sickness (DCS). Symptoms may include:")
        print("- Joint pain")
        print("- Numbness or tingling")
        print("- Dizziness")
        print("- Difficulty breathing")
        print("\nPlease follow the recommended surface interval guidelines")
        print("for your safety. Consider rebooking your flight if possible.")
    
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
