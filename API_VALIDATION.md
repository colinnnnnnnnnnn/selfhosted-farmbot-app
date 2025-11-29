# API Request/Response Serialization Validation

## Overview

The FarmBot API implements **comprehensive request validation** with detailed, actionable error messages. All input parameters are validated against FarmBot hardware constraints and safety limits before operations are executed.

## Features

✅ **Hardware-Aware Bounds Checking** - Coordinates, speeds, and depths validated against FarmBot Genesis XL workspace  
✅ **Clear Error Messages** - Shows expected range and actual value provided  
✅ **Type Safety** - Validates data types before processing  
✅ **Security Checks** - Blocks dangerous Lua commands  
✅ **Comprehensive Coverage** - Every operation has appropriate validation  

---

## Validation System Architecture

### Validator Classes (in `api/validators.py`)

Each validator is a reusable class that enforces specific constraints:

| Validator | Purpose | Constraints |
|-----------|---------|------------|
| `CoordinateValidator` | Position bounds checking | X: -100 to 3000mm, Y: -100 to 3000mm, Z: -400 to 100mm |
| `SpeedValidator` | Movement speed validation | 0-100% |
| `DepthValidator` | Tool insertion depth | -200 to 0mm (negative = down) |
| `VolumeValidator` | Liquid volume safety | 0.01-5000ml |
| `PinValidator` | GPIO pin validity | Only valid pins: 8, 9, 10, 11, 12, 59 |
| `AngleValidator` | Servo angle limits | 0-180 degrees |
| `LuaScriptValidator` | Script safety & length | Max 10,000 chars, forbids dangerous commands |
| `TimeValidator` | Duration limits | 0.1-3600 seconds |
| `CountValidator` | Quantity bounds | 1-10,000 items |

### Integration with Serializers

Each serializer now includes validators and docstrings:

```python
class PositionSerializer(serializers.Serializer):
    """Validates absolute movement coordinates and speed."""
    x = serializers.FloatField(required=True, validators=[custom_validator])
    y = serializers.FloatField(required=True)
    z = serializers.FloatField(required=True)
    speed = serializers.IntegerField(validators=[speed_validator])
    
    def validate(self, data):
        # Custom multi-field validation
        coordinate_validator(data)
        return data
```

---

## Example Error Messages

### Coordinate Out of Bounds
```bash
POST /api/move-absolute/
{
    "x": 5000,  # Exceeds max of 3000
    "y": 200,
    "z": -50
}

Response (400):
{
    "x": ["X-axis position must be between -100 and 3000, got 5000"]
}
```

### Invalid GPIO Pin
```bash
POST /api/servo-angle/
{
    "pin": 99,  # Invalid pin
    "angle": 90
}

Response (400):
{
    "pin": ["Invalid pin 99. Valid pins: 8(Water), 9(Vacuum), 10(Seed Injector), 11(Rotary Tool/Weeder), 12(Tool Verification), 59(Soil Sensor)"]
}
```

### Dangerous Lua Script
```bash
POST /api/lua-script/
{
    "lua_string": "os.execute('dangerous command')"
}

Response (400):
{
    "lua_string": ["Lua script contains forbidden command: os.execute"]
}
```

### Volume Out of Range
```bash
POST /api/dispense/
{
    "milliliters": 10000,  # Max is 5000
    "pin": 8
}

Response (400):
{
    "milliliters": ["Volume too large (max 5000ml per dispense), got 10000"]
}
```

### Missing Required Field
```bash
POST /api/move-absolute/
{
    "x": 100,
    "y": 200
    // Missing z
}

Response (400):
{
    "z": ["This field is required."]
}
```

---

## Validated Endpoints

### Movement Operations

#### Move Absolute
```
POST /api/move-absolute/
{
    "x": 100-3000,      # float, mm
    "y": 100-3000,      # float, mm
    "z": -400 to 100,   # float, mm
    "speed": 0-100      # int, %
}
```

#### Move Relative
```
POST /api/move-relative/
{
    "x": float,     # Relative movement
    "y": float,
    "z": float,
    "speed": 0-100
}
```

### Tool Operations

#### Servo Angle Control
```
POST /api/servo-angle/
{
    "pin": 8|9|10|11|12|59,  # Valid GPIO pins
    "angle": 0-180            # Servo position degrees
}
```

#### Water Plant
```
POST /api/water-plant/
{
    "x": 100-3000,        # Coordinates in mm
    "y": 100-3000,
    "z": -400 to 100,
}
```

#### Dispense Liquid
```
POST /api/dispense/
{
    "milliliters": 0.01-5000,           # Volume in ml
    "tool_name": "optional_tool_name",  # OR
    "pin": 8|9|10|11|12|59              # Required: either tool_name or pin
}
```

#### Weeding
```
POST /api/weeder/
{
    "x": 100-3000,          # Target location
    "y": 100-3000,
    "z": -400 to 100,
    "working_depth": -200 to 0,  # Negative = down
    "speed": 0-100               # Motor speed %
}
```

#### Rotary Tool
```
POST /api/rotary-tool/
{
    "speed": 0-100,         # Motor speed %
    "duration": 0.1-3600    # Seconds
}
```

#### Seed Injection
```
POST /api/seed-injector/
{
    "seeds_count": 1-10000,     # Number of seeds
    "dispense_time": 0.1-3600   # Seconds per seed
}
```

### Script Execution

#### Lua Script
```
POST /api/lua-script/
{
    "lua_string": "valid_lua_code"  # Max 10,000 chars
}

Forbidden commands:
- os.execute
- io.system
- load
- loadstring
- __G__
```

---

## Error Response Format

All validation errors follow this structure:

```json
{
    "field_name": ["Error message describing the problem"]
}
```

### Multiple Errors
```json
{
    "x": ["X-axis position must be between -100 and 3000, got 5000"],
    "speed": ["Speed must be between 0 and 100%, got 150"]
}
```

### Non-Field Errors
```json
{
    "non_field_errors": ["Either 'tool_name' or 'pin' must be specified"]
}
```

---

## Custom Validation Logic

### Coordinate Validation
```python
class CoordinateValidator:
    BOUNDS = {
        'x': {'min': -100, 'max': 3000},
        'y': {'min': -100, 'max': 3000},
        'z': {'min': -400, 'max': 100},
    }
```

### Pin Validation with Descriptions
```python
VALID_PINS = {
    8: 'Water',
    9: 'Vacuum',
    10: 'Seed Injector',
    11: 'Rotary Tool / Weeder',
    12: 'Tool Verification',
    59: 'Soil Sensor',
}
```

### Security Restrictions
```python
FORBIDDEN_KEYWORDS = [
    'os.execute',      # Execute system commands
    'io.system',       # File system access
    'load',            # Dynamic code loading
    'loadstring',      # Code from strings
    '__G__'            # Global table access
]
```

---

## Testing Validation

### Run Validation Tests
```bash
python manage.py test api.validation_tests -v 2
```

### Manual Testing with curl
```bash
# Invalid coordinate (out of bounds)
curl -X POST http://localhost:8000/api/move-absolute/ \
  -H "Content-Type: application/json" \
  -d '{"x": 5000, "y": 200, "z": -50}'

# Invalid pin
curl -X POST http://localhost:8000/api/servo-angle/ \
  -H "Content-Type: application/json" \
  -d '{"pin": 99, "angle": 90}'

# Dangerous Lua
curl -X POST http://localhost:8000/api/lua-script/ \
  -H "Content-Type: application/json" \
  -d '{"lua_string": "os.execute(\"rm -rf /\")"}'
```

---

## Frontend Integration

### Example: React with Validation Feedback

```javascript
async function moveBot(x, y, z) {
  try {
    const response = await fetch('/api/move-absolute/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ x, y, z })
    });

    if (!response.ok) {
      const errors = await response.json();
      // errors: { "x": ["X-axis position must be between ..."] }
      displayErrors(errors);
      return;
    }

    setStatus('Moving to (' + x + ', ' + y + ', ' + z + ')');
  } catch (error) {
    setStatus('Error: ' + error.message);
  }
}

function displayErrors(errors) {
  Object.entries(errors).forEach(([field, messages]) => {
    messages.forEach(msg => {
      showErrorNotification(field + ': ' + msg);
    });
  });
}
```

---

## Benefits

### For Developers
- **Clear API Contract** - Validators document expected inputs
- **Consistent Error Messages** - Users get same format everywhere
- **Easy to Extend** - Add new validators without changing views
- **Reusable Validation** - Same validator used in multiple endpoints

### For Users
- **Immediate Feedback** - Errors before operation starts
- **Actionable Messages** - Shows valid range and what was provided
- **Safety** - Prevents hardware damage from invalid commands
- **Security** - Blocks dangerous operations

### For System
- **Early Failure** - Catches bad data before database/hardware calls
- **Performance** - No wasted processing on invalid requests
- **Reliability** - Consistent validation across all endpoints
- **Auditability** - All validation attempts logged

---

## Future Enhancements

- [ ] Rate limiting per endpoint
- [ ] Coordinate workspace geometry checking
- [ ] Tool presence verification before operations
- [ ] Historical validation data for ML-based anomaly detection
- [ ] Batch operation validation
- [ ] Conditional validation based on bot state
