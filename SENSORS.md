/api/seed-injector/ (POST) - Uses the seed injector to plant seeds

Parameters:
seeds_count (optional, default: 1) - Number of seeds to plant
dispense_time (optional, default: 1.0) - Time in seconds for each seed dispensing action
/api/rotary-tool/ (POST) - Controls the rotary tool for operations like weeding or soil working

/api/rotary-tool/ (POST) - Controls the rotary tool for operations like weeding or soil working
Parameters:
speed (optional, default: 100) - Speed percentage (0-100)
duration (optional, default: 5.0) - How long to run the tool in seconds
/api/soil-sensor/ (GET) - Reads soil sensor data

/api/soil-sensor/ (GET) - Reads soil sensor data
Returns:
moisture - Soil moisture percentage (0-100)
raw_value - Raw sensor reading (0-1023)

/api/weeder/ (POST) - Controls the weeder tool
Parameters:
x (required): X coordinate for weeding
y (required): Y coordinate for weeding
z (required): Z coordinate approach height
working_depth (optional, default: -20): How deep to insert the weeder tool in mm
speed (optional, default: 100): Speed percentage for the rotary tool (0-100)