# geocalc
Online geographic calculator from David cross - converted to python and used for own purposes by Nolan Pearce N2WU

This script should run headless on a raspberry pi connected to antenna rotator, GPS, and gyroscope.

**When starting the script, the gyroscope should be as flat and stationary as possible and orientated compass (magnetic) north. The gyroscope will only read angular velocities on the z axis (rotation)**

The code requires you to put in your aprs.fi API key in the azel_calc.py script. My api key is there now. It asks for text input for callsign - you must change this if you want to run headless.

Accomplishes the following:
1. Takes input "station" GPS coordinates
2. Parses target GPS coordinates from APRS
3. Outputs elevation, azimuth, and distance 
4. Adjusts azimuth if device is rotated in any way
5. Adjusts antenna rotator to appropriate elevationand azimuth
