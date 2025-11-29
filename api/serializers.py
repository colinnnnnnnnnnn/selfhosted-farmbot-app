from rest_framework import serializers
from django.urls import reverse
from .models import Sequence, Step, Photo, NotificationPreference
from .validators import (
    coordinate_validator, speed_validator, depth_validator,
    volume_validator, pin_validator, angle_validator,
    lua_script_validator, time_validator, count_validator
)

class PhotoModelSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Photo
        fields = ['id', 'farmbot_id', 'created_at', 'coordinates', 'meta_data', 'url']
        read_only_fields = ['created_at']
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/farm_images/{obj.filename}')
        return f'/farm_images/{obj.filename}'

class PositionSerializer(serializers.Serializer):
    """Validates absolute movement coordinates and speed.
    
    Expected ranges:
    - x, y: -100 to 3000 mm
    - z: -400 to 100 mm (negative is down)
    - speed: 0-100%
    """
    x = serializers.FloatField(required=True, help_text="X coordinate in mm")
    y = serializers.FloatField(required=True, help_text="Y coordinate in mm")
    z = serializers.FloatField(required=True, help_text="Z coordinate in mm")
    speed = serializers.IntegerField(required=False, default=100, validators=[speed_validator])
    
    def validate(self, data):
        coordinate_validator(data)
        return data

class ServoAngleSerializer(serializers.Serializer):
    """Validates servo motor angle control.
    
    Pin should be a valid GPIO pin number.
    Angle: 0-180 degrees.
    """
    pin = serializers.IntegerField(required=True, validators=[pin_validator])
    angle = serializers.IntegerField(required=True, validators=[angle_validator])

class LuaScriptSerializer(serializers.Serializer):
    """Validates Lua script execution.
    
    Scripts are sandboxed and forbidden commands (os.execute, etc.) are blocked.
    Max length: 10000 characters.
    """
    lua_string = serializers.CharField(required=True, validators=[lua_script_validator])

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)

class PhotoSerializer(serializers.Serializer):
    url = serializers.URLField(read_only=True)

class WateringSerializer(serializers.Serializer):
    """Validates watering operation coordinates.
    
    Default values point to typical watering location.
    """
    x = serializers.FloatField(required=False, default=6, help_text="X coordinate in mm")
    y = serializers.FloatField(required=False, default=600, help_text="Y coordinate in mm")
    z = serializers.FloatField(required=False, default=-340, help_text="Z coordinate in mm")
    
    def validate(self, data):
        coordinate_validator(data)
        return data

class DispensingSerializer(serializers.Serializer):
    """Validates liquid dispensing operations.
    
    Volume: 0.01-5000 ml
    Either tool_name or pin must be specified.
    """
    milliliters = serializers.FloatField(required=True, validators=[volume_validator])
    tool_name = serializers.CharField(required=False, allow_blank=False)
    pin = serializers.IntegerField(required=False, validators=[pin_validator])
    
    def validate(self, data):
        if not data.get('tool_name') and not data.get('pin'):
            raise serializers.ValidationError(
                "Either 'tool_name' or 'pin' must be specified"
            )
        return data

class ToolSerializer(serializers.Serializer):
    tool_name = serializers.CharField(required=True)

class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['id', 'command', 'parameters', 'order']

class SeedInjectorSerializer(serializers.Serializer):
    """Validates seed injection operations.
    
    Count: 1-10000 seeds
    Time: 0.1-3600 seconds per seed
    """
    seeds_count = serializers.IntegerField(required=False, default=1, validators=[count_validator])
    dispense_time = serializers.FloatField(required=False, default=1.0, validators=[time_validator])

class RotaryToolSerializer(serializers.Serializer):
    """Validates rotary tool operations (weeding, tilling, etc.).
    
    Speed: 0-100%
    Duration: 0.1-3600 seconds
    """
    speed = serializers.IntegerField(required=False, default=100, validators=[speed_validator])
    duration = serializers.FloatField(required=False, default=5.0, validators=[time_validator])

class SoilSensorSerializer(serializers.Serializer):
    moisture = serializers.FloatField(read_only=True)
    raw_value = serializers.IntegerField(read_only=True)

class WeederSerializer(serializers.Serializer):
    """Validates weeding tool operations.
    
    Coordinates define weed location.
    Working depth: -200 to 0 mm (negative = down)
    Speed: 0-100%
    """
    x = serializers.FloatField(required=True, help_text="X coordinate in mm")
    y = serializers.FloatField(required=True, help_text="Y coordinate in mm")
    z = serializers.FloatField(required=True, help_text="Z coordinate in mm")
    working_depth = serializers.FloatField(required=False, default=-20, validators=[depth_validator])
    speed = serializers.IntegerField(required=False, default=100, validators=[speed_validator])
    
    def validate(self, data):
        coordinate_validator(data)
        return data

class SequenceSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True)

    class Meta:
        model = Sequence
        fields = ['id', 'name', 'steps']

    def create(self, validated_data):
        steps_data = validated_data.pop('steps')
        sequence = Sequence.objects.create(**validated_data)
        for step_data in steps_data:
            Step.objects.create(sequence=sequence, **step_data)
        return sequence

    def update(self, instance, validated_data):
        steps_data = validated_data.pop('steps')
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # Simple update: delete old steps and create new ones
        instance.steps.all().delete()
        for step_data in steps_data:
            Step.objects.create(sequence=instance, **step_data)

        return instance

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['enabled', 'report_frequency']