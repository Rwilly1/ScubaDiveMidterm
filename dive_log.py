"""
Dive Log Management System

This module provides a comprehensive system for creating, storing, and managing scuba diving logs.
It includes functionality for:
- Creating detailed dive log entries with extensive metadata
- Storing dive logs in a JSON file
- Loading and displaying dive log history
- Tracking various dive parameters including:
  * Depth and time information
  * Environmental conditions
  * Equipment used
  * Gas consumption
  * Exposure protection
  * Verification details
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import os
import uuid

@dataclass
class DiveLog:
    """
    A comprehensive dive log entry containing all relevant information about a dive.
    
    Attributes:
        diver_name (str): Name of the diver
        dive_number (int): Sequential number of this dive
        date (str): Date of the dive in YYYY-MM-DD format
        location (str): Dive site location
        depth_avg (float): Average depth in feet
        depth_max (float): Maximum depth reached in feet
        bottom_time (int): Total time spent underwater in minutes
        safety_stop_time (int): Time spent at safety stop in minutes
        rnt (int): Residual Nitrogen Time from previous dive
        abt (int): Actual Bottom Time of this dive
        tbt (int): Total Bottom Time (RNT + ABT)
        dive_type (List[str]): Characteristics of dive (Fresh/Salt, Shore/Boat, etc.)
        activities (List[str]): Activities performed during dive
        temperature_air (float): Air temperature
        temperature_surface (float): Water temperature at surface
        temperature_bottom (float): Water temperature at depth
        visibility_ft (float): Underwater visibility in feet
        air_start_psi (int): Starting air pressure in PSI
        air_end_psi (int): Ending air pressure in PSI
        gas_type (str): Type of breathing gas used (Air/Nitrox)
        weight_lbs (float): Amount of weight used in pounds
        weight_adjustment (str): Weight adjustment indicator (+/-/)
        exposure_protection (Dict[str, float]): Type and thickness of exposure protection
        equipment_used (List[str]): Special equipment used during dive
        verification_type (str): Type of dive verification
        certification_number (str): Certifier's certification number
        nitrox_percentage (Optional[int]): Percentage of oxygen if Nitrox used
        id (Optional[str]): Unique identifier for the dive log
        created_at (Optional[str]): Timestamp when log was created
    """
    diver_name: str
    dive_number: int
    date: str
    location: str
    depth_avg: float
    depth_max: float
    bottom_time: int
    safety_stop_time: int
    rnt: int  # Residual Nitrogen Time
    abt: int  # Actual Bottom Time
    tbt: int  # Total Bottom Time
    dive_type: List[str]  # Fresh/Salt, Shore/Boat, Deep/Night
    activities: List[str]  # Recreation, Wreck, Reef, Cave, Search&Recov, UW Photo, UW Navig
    temperature_air: float
    temperature_surface: float
    temperature_bottom: float
    visibility_ft: float
    air_start_psi: int
    air_end_psi: int
    gas_type: str  # Air or Nitrox
    weight_lbs: float
    weight_adjustment: str  # +, -, or 
    exposure_protection: Dict[str, float]  # Dict of protection type and mm thickness
    equipment_used: List[str]  # Camera, Computer, Flashlight
    verification_type: str  # Instructor, Divemaster, or Buddy
    certification_number: str
    nitrox_percentage: Optional[int] = None
    id: Optional[str] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        """
        Initialize unique identifier and timestamp for new dive logs.
        Called automatically after the dataclass is initialized.
        """
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the dive log to a dictionary format for JSON serialization.
        Ensures id and created_at are at the start of the dictionary for readability.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the dive log
        """
        data = asdict(self)
        if 'id' in data:
            id_value = data.pop('id')
            data = {'id': id_value, **data}
        if 'created_at' in data:
            created_at_value = data.pop('created_at')
            data = {'created_at': created_at_value, **data}
        return data

def get_dive_log_input() -> DiveLog:
    """
    Get dive log information from user input.
    
    Returns:
        DiveLog: A new dive log object based on user input
    """
    print("\n=== Dive Log Entry ===\n")
    
    # Basic dive info
    diver_name = input("Diver Name: ")
    dive_number = int(input("Dive #: "))
    date = input("Date (YYYY-MM-DD): ")
    location = input("Location: ")
    
    # Depth and time
    depth_avg = float(input("\nAverage Depth (ft): "))
    depth_max = float(input("Maximum Depth (ft): "))
    bottom_time = int(input("Bottom Time (mins): "))
    safety_stop_time = int(input("Safety Stop Time (mins): "))
    rnt = int(input("Residual Nitrogen Time (RNT): "))
    abt = int(input("Actual Bottom Time (ABT): "))
    tbt = rnt + abt
    
    # Environment type
    print("\nDive Type (enter y/n for each):")
    dive_type = []
    for type_option in ["Fresh", "Salt", "Shore", "Boat", "Deep", "Night"]:
        if input(f"{type_option}? (y/n): ").lower() == 'y':
            dive_type.append(type_option)
    
    # Activities
    print("\nActivities (enter y/n for each):")
    activities = []
    activity_options = ["Recreation", "Wreck", "Reef", "Cave", 
                       "Search & Recovery", "UW Photo", "UW Navigation"]
    for activity in activity_options:
        if input(f"{activity}? (y/n): ").lower() == 'y':
            activities.append(activity)
    
    # Conditions
    print("\nTemperatures:")
    temp_air = float(input("Air temperature: "))
    temp_surface = float(input("Surface temperature: "))
    temp_bottom = float(input("Bottom temperature: "))
    visibility = float(input("\nVisibility (ft): "))
    
    # Air/Gas
    print("\nAir/Gas:")
    air_start = int(input("Starting pressure (psi): "))
    air_end = int(input("Ending pressure (psi): "))
    gas_type = input("Gas type (Air/Nitrox): ").capitalize()
    nitrox_percent = None
    if gas_type == "Nitrox":
        nitrox_percent = int(input("Nitrox percentage: "))
    
    # Weight and Protection
    weight = float(input("\nWeight (lbs): "))
    weight_adj = input("Weight adjustment (+/-/): ")
    
    print("\nExposure Protection (thickness in mm, 0 if not used):")
    protection = {}
    for item in ["Full", "Shorty", "Boots", "Hood", "Gloves"]:
        thickness = float(input(f"{item} thickness (mm): "))
        if thickness > 0:
            protection[item] = thickness
    
    # Equipment
    print("\nEquipment Used (y/n for each):")
    equipment = []
    for item in ["Camera", "Computer", "Flashlight"]:
        if input(f"{item}? (y/n): ").lower() == 'y':
            equipment.append(item)
    
    # Verification
    print("\nVerification:")
    ver_options = ["Instructor", "Divemaster", "Buddy"]
    ver_type = ""
    for i, option in enumerate(ver_options, 1):
        print(f"{i}. {option}")
    while ver_type not in ver_options:
        try:
            choice = int(input("Choose verification type (1-3): "))
            ver_type = ver_options[choice-1]
        except (ValueError, IndexError):
            print("Invalid choice. Please enter 1, 2, or 3.")
    
    cert_num = input("Certification #: ")
    
    return DiveLog(
        diver_name=diver_name,
        dive_number=dive_number,
        date=date,
        location=location,
        depth_avg=depth_avg,
        depth_max=depth_max,
        bottom_time=bottom_time,
        safety_stop_time=safety_stop_time,
        rnt=rnt,
        abt=abt,
        tbt=tbt,
        dive_type=dive_type,
        activities=activities,
        temperature_air=temp_air,
        temperature_surface=temp_surface,
        temperature_bottom=temp_bottom,
        visibility_ft=visibility,
        air_start_psi=air_start,
        air_end_psi=air_end,
        gas_type=gas_type,
        nitrox_percentage=nitrox_percent,
        weight_lbs=weight,
        weight_adjustment=weight_adj,
        exposure_protection=protection,
        equipment_used=equipment,
        verification_type=ver_type,
        certification_number=cert_num
    )

def save_dive_log(dive_log: DiveLog) -> None:
    """
    Save dive log to JSON file.
    
    Args:
        dive_log (DiveLog): The dive log to save
    """
    try:
        with open("dive_logs.json", "r") as f:
            logs = json.load(f)
            # Update existing logs with IDs if they don't have them
            for log in logs:
                if 'id' not in log:
                    log['id'] = str(uuid.uuid4())
                if 'created_at' not in log:
                    log['created_at'] = datetime.now().isoformat()
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []
    
    # Add the new log
    logs.append(dive_log.to_dict())
    
    with open("dive_logs.json", "w") as f:
        json.dump(logs, f, indent=2)

def load_dive_logs() -> List[Dict[str, Any]]:
    """
    Load dive logs from JSON file.
    
    Returns:
        List[Dict[str, Any]]: List of dive logs
    """
    try:
        with open("dive_logs.json", "r") as f:
            logs = json.load(f)
            # Update logs with missing IDs
            modified = False
            for log in logs:
                if 'id' not in log:
                    log['id'] = str(uuid.uuid4())
                    modified = True
                if 'created_at' not in log:
                    log['created_at'] = datetime.now().isoformat()
                    modified = True
            
            # Save if we had to add any IDs
            if modified:
                with open("dive_logs.json", "w") as f:
                    json.dump(logs, f, indent=2)
            return logs
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def print_dive_log(dive_log: DiveLog) -> None:
    """
    Print formatted dive log report.
    
    Args:
        dive_log (DiveLog): The dive log to print
    """
    print("\n" + "="*50)
    print(f"DIVE LOG REPORT #{dive_log.dive_number} - {dive_log.diver_name}")
    print("="*50)
    
    print(f"\nDate: {dive_log.date}")
    print(f"Location: {dive_log.location}")
    
    print("\nDEPTH & TIME")
    print(f"Average Depth: {dive_log.depth_avg} ft")
    print(f"Maximum Depth: {dive_log.depth_max} ft")
    print(f"Bottom Time: {dive_log.bottom_time} mins")
    print(f"Safety Stop: {dive_log.safety_stop_time} mins")
    print(f"Total Bottom Time: {dive_log.tbt} mins (RNT: {dive_log.rnt} + ABT: {dive_log.abt})")
    
    print("\nENVIRONMENT")
    print(f"Type: {', '.join(dive_log.dive_type)}")
    print(f"Activities: {', '.join(dive_log.activities)}")
    
    print("\nCONDITIONS")
    print(f"Temperature - Air: {dive_log.temperature_air}°F")
    print(f"Temperature - Surface: {dive_log.temperature_surface}°F")
    print(f"Temperature - Bottom: {dive_log.temperature_bottom}°F")
    print(f"Visibility: {dive_log.visibility_ft} ft")
    
    print("\nAIR/GAS")
    print(f"Start Pressure: {dive_log.air_start_psi} psi")
    print(f"End Pressure: {dive_log.air_end_psi} psi")
    print(f"Gas Type: {dive_log.gas_type}")
    if dive_log.nitrox_percentage:
        print(f"Nitrox: {dive_log.nitrox_percentage}%")
    
    print("\nWEIGHT & PROTECTION")
    print(f"Weight: {dive_log.weight_lbs} lbs ({dive_log.weight_adjustment})")
    print("Protection:")
    for item, thickness in dive_log.exposure_protection.items():
        print(f"  - {item}: {thickness}mm")
    
    print("\nEQUIPMENT")
    print(f"Used: {', '.join(dive_log.equipment_used)}")
    
    print("\nVERIFICATION")
    print(f"Type: {dive_log.verification_type}")
    print(f"Certification #: {dive_log.certification_number}")
    print("\n" + "="*50 + "\n")

def main() -> None:
    """
    Main entry point of the program.
    """
    try:
        # Get dive log information
        dive_log = get_dive_log_input()
        
        # Save to file
        save_dive_log(dive_log)
        
        # Print report
        print_dive_log(dive_log)
        
        print("Dive log has been saved successfully!")
        
    except KeyboardInterrupt:
        print("\n\nDive log entry cancelled.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Dive log entry failed.")

if __name__ == "__main__":
    main()
