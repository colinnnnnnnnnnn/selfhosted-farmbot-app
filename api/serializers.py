from rest_framework import serializers

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