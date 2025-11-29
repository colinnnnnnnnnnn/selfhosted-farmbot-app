"""
Custom validators for API request/response validation.
Provides detailed error messages and bounds checking for FarmBot operations.
"""

from rest_framework import serializers
from decimal import Decimal


class CoordinateValidator:
    """Validates FarmBot coordinate values (X, Y, Z positions)"""
    
    # FarmBot Genesis XL typical workspace (in mm)
    BOUNDS = {
        'x': {'min': -100, 'max': 3000, 'description': 'X-axis position'},
        'y': {'min': -100, 'max': 3000, 'description': 'Y-axis position'},
        'z': {'min': -400, 'max': 100, 'description': 'Z-axis position (negative is down)'},
    }
    
    def __call__(self, data):
        """Validate coordinate object"""
        for axis in ['x', 'y', 'z']:
            if axis not in data:
                continue
                
            value = data[axis]
            bounds = self.BOUNDS[axis]
            
            if not isinstance(value, (int, float, Decimal)):
                raise serializers.ValidationError(
                    {axis: f"{bounds['description']} must be a number, got {type(value).__name__}"}
                )
            
            if value < bounds['min'] or value > bounds['max']:
                raise serializers.ValidationError(
                    {axis: f"{bounds['description']} must be between {bounds['min']} and {bounds['max']}, got {value}"}
                )


class SpeedValidator:
    """Validates movement speed (0-100%)"""
    
    def __call__(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError(
                f"Speed must be an integer, got {type(value).__name__}"
            )
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                f"Speed must be between 0 and 100%, got {value}"
            )


class DepthValidator:
    """Validates tool working depth"""
    
    def __call__(self, value):
        if not isinstance(value, (int, float, Decimal)):
            raise serializers.ValidationError(
                f"Depth must be a number, got {type(value).__name__}"
            )
        # Depth should be negative (going down) and reasonable
        if value > 0:
            raise serializers.ValidationError(
                f"Working depth should be negative (going down), got {value}"
            )
        if value < -200:
            raise serializers.ValidationError(
                f"Working depth too deep (max 200mm), got {value}"
            )


class VolumeValidator:
    """Validates liquid volume for watering/dispensing"""
    
    def __call__(self, value):
        if not isinstance(value, (int, float, Decimal)):
            raise serializers.ValidationError(
                f"Volume must be a number, got {type(value).__name__}"
            )
        if value < 0.01:
            raise serializers.ValidationError(
                f"Volume must be at least 0.01ml, got {value}"
            )
        if value > 5000:
            raise serializers.ValidationError(
                f"Volume too large (max 5000ml per dispense), got {value}"
            )


class PinValidator:
    """Validates GPIO pin numbers"""
    
    VALID_PINS = {
        8: 'Water',
        9: 'Vacuum',
        10: 'Seed Injector',
        11: 'Rotary Tool / Weeder',
        12: 'Tool Verification',
        59: 'Soil Sensor',
    }
    
    def __call__(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError(
                f"Pin must be an integer, got {type(value).__name__}"
            )
        if value not in self.VALID_PINS:
            valid_pins_str = ', '.join(f"{pin}({self.VALID_PINS[pin]})" for pin in sorted(self.VALID_PINS.keys()))
            raise serializers.ValidationError(
                f"Invalid pin {value}. Valid pins: {valid_pins_str}"
            )


class AngleValidator:
    """Validates servo angle (0-180 degrees)"""
    
    def __call__(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError(
                f"Angle must be an integer, got {type(value).__name__}"
            )
        if value < 0 or value > 180:
            raise serializers.ValidationError(
                f"Servo angle must be between 0 and 180 degrees, got {value}"
            )


class LuaScriptValidator:
    """Validates Lua script input"""
    
    MAX_LENGTH = 10000
    FORBIDDEN_KEYWORDS = ['os.execute', 'io.system', 'load', 'loadstring', '__G__']
    
    def __call__(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError(
                f"Lua script must be a string, got {type(value).__name__}"
            )
        
        if len(value) == 0:
            raise serializers.ValidationError("Lua script cannot be empty")
        
        if len(value) > self.MAX_LENGTH:
            raise serializers.ValidationError(
                f"Lua script too long (max {self.MAX_LENGTH} characters), got {len(value)}"
            )
        
        # Check for forbidden system commands
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in value:
                raise serializers.ValidationError(
                    f"Lua script contains forbidden command: {keyword}"
                )


class TimeValidator:
    """Validates time duration values"""
    
    def __call__(self, value):
        if not isinstance(value, (int, float, Decimal)):
            raise serializers.ValidationError(
                f"Time must be a number, got {type(value).__name__}"
            )
        if value < 0.1:
            raise serializers.ValidationError(
                f"Time must be at least 0.1 seconds, got {value}"
            )
        if value > 3600:  # 1 hour max
            raise serializers.ValidationError(
                f"Time too long (max 3600 seconds), got {value}"
            )


class CountValidator:
    """Validates count/quantity values"""
    
    def __call__(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError(
                f"Count must be an integer, got {type(value).__name__}"
            )
        if value < 1:
            raise serializers.ValidationError(
                f"Count must be at least 1, got {value}"
            )
        if value > 10000:
            raise serializers.ValidationError(
                f"Count too large (max 10000), got {value}"
            )


# Instantiate validators for reuse
coordinate_validator = CoordinateValidator()
speed_validator = SpeedValidator()
depth_validator = DepthValidator()
volume_validator = VolumeValidator()
pin_validator = PinValidator()
angle_validator = AngleValidator()
lua_script_validator = LuaScriptValidator()
time_validator = TimeValidator()
count_validator = CountValidator()
