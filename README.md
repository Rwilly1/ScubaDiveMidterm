# PADI Dive Planner Calculator

A Python implementation of the PADI Recreational Dive Planner that helps calculate:
- Pressure groups for single and repetitive dives
- Surface interval requirements
- Residual nitrogen times
- No-decompression limits

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # On Unix/macOS
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

## Usage

Run the program:
```bash
python divetable.py
```

Follow the prompts to:
1. Enter first dive depth and time
2. Input surface interval
3. Plan second dive depth and time

The program will:
- Calculate pressure groups
- Check no-decompression limits
- Compute residual nitrogen time
- Validate dive plan safety

## Safety Notice

This is an educational implementation and should not be used for actual dive planning. Always consult official PADI dive tables and a certified diving instructor for actual dive planning.
