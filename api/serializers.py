from rest_framework import serializers
from .models import Sequence, Step

class PositionSerializer(serializers.Serializer):
    x = serializers.FloatField(required=True)
    y = serializers.FloatField(required=True)
    z = serializers.FloatField(required=True)
    speed = serializers.IntegerField(required=False)

class ServoAngleSerializer(serializers.Serializer):
    pin = serializers.IntegerField(required=True)
    angle = serializers.IntegerField(required=True)

class LuaScriptSerializer(serializers.Serializer):
    lua_string = serializers.CharField(required=True)

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)

class PhotoSerializer(serializers.Serializer):
    url = serializers.URLField(read_only=True)

class WateringSerializer(serializers.Serializer):
    x = serializers.IntegerField(required=False, default=6)
    y = serializers.IntegerField(required=False, default=600)
    z = serializers.IntegerField(required=False, default=-340)

class DispensingSerializer(serializers.Serializer):
    milliliters = serializers.FloatField(required=True, min_value=0.1)
    tool_name = serializers.CharField(required=False)
    pin = serializers.IntegerField(required=False)

class ToolSerializer(serializers.Serializer):
    tool_name = serializers.CharField(required=True)

class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['id', 'command', 'parameters', 'order']

class SeedInjectorSerializer(serializers.Serializer):
    seeds_count = serializers.IntegerField(required=False, default=1, min_value=1)
    dispense_time = serializers.FloatField(required=False, default=1.0, min_value=0.1)

class RotaryToolSerializer(serializers.Serializer):
    speed = serializers.IntegerField(required=False, default=100, min_value=0, max_value=100)
    duration = serializers.FloatField(required=False, default=5.0, min_value=0.1)

class SoilSensorSerializer(serializers.Serializer):
    moisture = serializers.FloatField(read_only=True)
    raw_value = serializers.IntegerField(read_only=True)

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