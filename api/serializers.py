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

 