import os
import zipfile
import io
# Export all photos as a ZIP file
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_photos_zip_view(request):
    try:
        images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'farm_images')
        if not os.path.exists(images_dir):
            return Response({"error": "farm_images directory not found"}, status=status.HTTP_404_NOT_FOUND)
        image_files = [f for f in os.listdir(images_dir) if f.lower().endswith('.jpg')]
        if not image_files:
            return Response({"error": "No .jpg images found"}, status=status.HTTP_404_NOT_FOUND)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for filename in image_files:
                file_path = os.path.join(images_dir, filename)
                zip_file.write(file_path, arcname=filename)
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="farmbot-photos.zip"'
        return response
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from .models import AuditLog
import csv
from django.http import HttpResponse
# Export audit logs as CSV
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_auditlog_view(request):
    try:
        format = request.query_params.get('format', 'csv')
        logs = AuditLog.objects.all().order_by('-timestamp')
        if not logs.exists():
            return Response({"error": "No audit logs found"}, status=status.HTTP_404_NOT_FOUND)
        if format == 'log':
            response = HttpResponse(content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="auditlog.log"'
            for log in logs:
                line = f"{log.timestamp} | {log.user.username if log.user else ''} | {log.action} | {log.object_id} | {log.details}\n"
                response.write(line)
            return response
        else:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="auditlog.csv"'
            writer = csv.writer(response)
            writer.writerow(['timestamp', 'user', 'action', 'object_id', 'details'])
            for log in logs:
                writer.writerow([
                    log.timestamp,
                    log.user.username if log.user else '',
                    log.action,
                    log.object_id,
                    log.details
                ])
            return response
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
import threading
import time
from .models import Sequence, Step, Photo
from .serializers import (
    PositionSerializer, ServoAngleSerializer, MessageSerializer, 
    LuaScriptSerializer, WateringSerializer, DispensingSerializer,
    ToolSerializer, SequenceSerializer, SeedInjectorSerializer,
    RotaryToolSerializer, SoilSensorSerializer, PhotoModelSerializer,
    WeederSerializer
)
from farmlib.wrapper import (
    connect_bot, move_absolute, move_relative, emergency_lock, emergency_unlock,
    find_home, go_to_home, power_off, reboot, servo_angle, lua_script, 
    get_position, send_message, take_photo, water_plant, mount_tool, 
    dismount_tool, dispense, use_seed_injector, use_rotary_tool, read_soil_sensor,
    use_weeder
)

# Initialize bot connection when server starts
connection_thread = threading.Thread(target=connect_bot)
connection_thread.daemon = True
connection_thread.start()

class PhotoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and managing photos taken by the FarmBot.
    """
    queryset = Photo.objects.all()
    serializer_class = PhotoModelSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        photo = self.get_object()
        try:
            # Delete the actual file
            import os
            if os.path.exists(photo.image_path):
                os.remove(photo.image_path)
            # Delete the database entry
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"error": f"Failed to delete photo: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SequenceViewSet(viewsets.ModelViewSet):
    serializer_class = SequenceSerializer
    permission_classes = [IsAuthenticated]

    COMMAND_MAP = {
        'move_absolute': move_absolute,
        'move_relative': move_relative,
        'water_plant': water_plant,
        'dispense': dispense,
        'take_photo': take_photo,
        'mount_tool': mount_tool,
        'dismount_tool': dismount_tool,
        'emergency_lock': emergency_lock,
        'emergency_unlock': emergency_unlock,
        'find_home': find_home,
        'go_to_home': go_to_home,
        'power_off': power_off,
        'reboot': reboot,
        'servo_angle': servo_angle,
        'lua_script': lua_script,
        'send_message': send_message,
    }

    def get_queryset(self):
        return Sequence.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        sequence = self.get_object()
        for step in sequence.steps.all():
            command_func = self.COMMAND_MAP.get(step.command)
            if not command_func:
                return Response({'error': f'Unknown command: {step.command}'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                print(f"Executing command: {step.command} with params: {step.parameters}")
                command_func(**step.parameters)
                # Default wait time, can be overridden by step parameter
                wait_time = step.parameters.get('wait', 2)
                time.sleep(wait_time)
            except Exception as e:
                return Response({'error': f'Failed to execute step {step.order} ({step.command}): {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'status': 'sequence executed'}, status=status.HTTP_200_OK)


@login_required
def social_auth_callback_view(request):
    if not connect_bot():
        return render(request, 'social_auth_callback.html', {
            'error': 'Could not connect to FarmBot. Please check credentials and network.'
        })
    token, _ = Token.objects.get_or_create(user=request.user)
    user_data = {
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
    }
    return render(request, 'social_auth_callback.html', {
        'token': token.key,
        'user': json.dumps(user_data)
    })

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def register_view(request):
    username = request.data.get('username') or request.data.get('email')
    email = request.data.get('email') or username
    password = request.data.get('password')
    errors = {}
    if not username or not password:
        errors['fields'] = "username/email and password are required"
    if username and not isinstance(username, str):
        errors['username'] = "username must be a string"
    if password and (not isinstance(password, str) or len(password) < 4):
        errors['password'] = "password must be at least 4 characters"
    if email and not isinstance(email, str):
        errors['email'] = "email must be a string"
    if User.objects.filter(username=username).exists():
        errors['username_exists'] = "username already exists"
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=username, email=email, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    # Audit log registration
    from .models import AuditLog
    AuditLog.objects.create(user=user, action="register", object_id=str(user.id), details=f"User {username} registered.")
    return Response({"token": token.key}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def login_view(request):
    username = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')
    errors = {}
    if not username or not password:
        errors['fields'] = "username/email and password are required"
    if username and not isinstance(username, str):
        errors['username'] = "username must be a string"
    if password and (not isinstance(password, str) or len(password) < 4):
        errors['password'] = "password must be at least 4 characters"
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    from .models import AuditLog
    if not user:
        AuditLog.objects.create(user=None, action="login_failed", details=f"Login failed for username: {username}")
        return Response({"error": "invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    if not connect_bot():
        AuditLog.objects.create(user=user, action="login_failed", object_id=str(user.id), details="Could not connect to FarmBot")
        return Response({"error": "Could not connect to FarmBot"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    token, _ = Token.objects.get_or_create(user=user)
    AuditLog.objects.create(user=user, action="login", object_id=str(user.id), details=f"User {username} logged in.")
    return Response({"token": token.key}, status=status.HTTP_200_OK)

@api_view(['POST'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def logout_view(request):
    try:
        Token.objects.filter(user=request.user).delete()
        return Response({"status": "logged out"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def me_view(request):
    user = request.user
    return Response({"id": user.id, "username": user.username, "email": user.email}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def connect_view(request):
    """Connect to FarmBot"""
    try:
        connect_bot()
        return Response({"status": "connected"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def move_absolute_view(request):
    """Move FarmBot to absolute position"""
    serializer = PositionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    # Validate coordinates and speed
    errors = {}
    for axis in ['x', 'y', 'z']:
        if not isinstance(data[axis], (int, float)):
            errors[axis] = f"{axis} must be a number"
    speed = data.get('speed', 100)
    if not isinstance(speed, (int, float)) or speed < 1 or speed > 100:
        errors['speed'] = "Speed must be between 1 and 100"
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        move_absolute(data['x'], data['y'], data['z'], speed)
        return Response({"status": "moving"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def move_relative_view(request):
    """Move FarmBot relative to current position"""
    serializer = PositionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    # Validate coordinates and speed
    errors = {}
    for axis in ['x', 'y', 'z']:
        if not isinstance(data[axis], (int, float)):
            errors[axis] = f"{axis} must be a number"
    speed = data.get('speed', 100)
    if not isinstance(speed, (int, float)) or speed < 1 or speed > 100:
        errors['speed'] = "Speed must be between 1 and 100"
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        move_relative(data['x'], data['y'], data['z'], speed)
        return Response({"status": "moving"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def emergency_lock_view(request):
    """Emergency lock FarmBot"""
    try:
        emergency_lock()
        return Response({"status": "locked"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def emergency_unlock_view(request):
    """Emergency unlock FarmBot"""
    try:
        emergency_unlock()
        return Response({"status": "unlocked"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def find_home_view(request):
    """Find home position"""
    try:
        find_home()
        return Response({"status": "finding home"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def go_to_home_view(request):
    """Go to home position"""
    try:
        go_to_home()
        return Response({"status": "moving to home"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def power_off_view(request):
    """Power off FarmBot"""
    try:
        power_off()
        return Response({"status": "powered off"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def reboot_view(request):
    """Reboot FarmBot"""
    try:
        reboot()
        return Response({"status": "rebooting"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def servo_angle_view(request):
    """Set servo angle"""
    serializer = ServoAngleSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    errors = {}
    pin = data.get('pin')
    angle = data.get('angle')
    if not isinstance(pin, int) or pin < 0 or pin > 20:
        errors['pin'] = "pin must be an integer between 0 and 20"
    if not isinstance(angle, (int, float)) or angle < 0 or angle > 180:
        errors['angle'] = "angle must be between 0 and 180"
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        servo_angle(pin, angle)
        return Response({"status": "servo angle set"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def lua_script_view(request):
    """Execute Lua script"""
    serializer = LuaScriptSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        data = serializer.validated_data
        lua_script(data['lua_string'])
        return Response({"status": "lua script executed"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def get_position_view(request):
    """Get current position"""
    try:
        position = get_position()
        if position is None:
            return Response({"error": "Could not get position"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(position, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def send_message_view(request):
    """Send message to FarmBot"""
    serializer = MessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        data = serializer.validated_data
        send_message(data['message'])
        return Response({"status": "message sent"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def mount_tool_view(request):
    """Mount a specific tool"""
    serializer = ToolSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    tool_name = data.get('tool_name')
    if not tool_name or not isinstance(tool_name, str):
        return Response({'tool_name': 'tool_name must be a non-empty string'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        success = mount_tool(tool_name=tool_name)
        if success:
            return Response({"status": "tool mounted"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to mount tool"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def dismount_tool_view(request):
    """Dismount the current tool"""
    try:
        success = dismount_tool()
        if success:
            return Response({"status": "tool dismounted"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to dismount tool"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def water_plant_view(request):
    """Move to position and water using FarmBot's built-in watering command"""
    serializer = WateringSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    # Validate coordinates
    errors = {}
    for axis in ['x', 'y', 'z']:
        val = data.get(axis, None)
        if val is not None and not isinstance(val, (int, float)):
            errors[axis] = f"{axis} must be a number"
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        success = water_plant(
            x=data.get('x', 6),
            y=data.get('y', 600),
            z=data.get('z', -340)
        )
        if success:
            return Response({"status": "watering completed"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Watering failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def dispense_view(request):
    """Dispense a specific amount of liquid"""
    serializer = DispensingSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    errors = {}
    milliliters = data.get('milliliters')
    if not isinstance(milliliters, (int, float)) or milliliters <= 0:
        errors['milliliters'] = "milliliters must be a positive number"
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        success = dispense(
            milliliters=milliliters,
            tool_name=data.get('tool_name'),
            pin=data.get('pin')
        )
        if success:
            return Response({"status": "dispensing completed"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Dispensing failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def take_photo_view(request):
    """Take a photo using FarmBot's camera and retrieve the most recent photo from FarmBot Web App"""
    try:
        result = take_photo()
        if result is None:
            return Response({"error": "Could not take photo"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Get current position for photo metadata
        position = get_position()
        coordinates = {}
        if position:
            coordinates = {
                'x': position[0],
                'y': position[1],
                'z': position[2]
            }

        # Create photo record with the most recent photo ID
        photo = Photo.objects.create(
            image_path=f"farm_images/image_{result['id']}.jpg",
            farmbot_id=result['id'],
            coordinates=coordinates,
            meta_data={
                'content_type': result['content_type'],
                'source': 'farmbot_web_app'
            }
        )
        
        # Check response format
        response_format = request.query_params.get('format', 'json')
        
        if response_format == 'json':
            serializer = PhotoModelSerializer(photo, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Return the image directly
            from django.http import HttpResponse
            return HttpResponse(
                result['image'],
                content_type=result['content_type']
            )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def clear_photos_view(request):
    """Clear all photos from the farm_images folder"""
    import os
    import glob
    
    try:
        # Get the farm_images directory path
        farm_images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'farm_images')
        
        # Find all image files
        image_patterns = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
        deleted_count = 0
        
        for pattern in image_patterns:
            files = glob.glob(os.path.join(farm_images_dir, pattern))
            for file_path in files:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except OSError as e:
                    print(f"Error deleting {file_path}: {e}")
        
        return Response({
            "message": f"Successfully deleted {deleted_count} photos",
            "deleted_count": deleted_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def seed_injector_view(request):
    """Use the seed injector to plant seeds"""
    serializer = SeedInjectorSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    errors = {}
    seeds_count = data.get('seeds_count', 1)
    dispense_time = data.get('dispense_time', 1.0)
    if not isinstance(seeds_count, int) or seeds_count < 1:
        errors['seeds_count'] = "seeds_count must be a positive integer"
    if not isinstance(dispense_time, (int, float)) or dispense_time <= 0:
        errors['dispense_time'] = "dispense_time must be a positive number"
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        success = use_seed_injector(
            seeds_count=seeds_count,
            dispense_time=dispense_time
        )
        if success:
            return Response({"status": "seeds planted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to plant seeds"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def rotary_tool_view(request):
    """Use the rotary tool"""
    serializer = RotaryToolSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    errors = {}
    speed = data.get('speed', 100)
    duration = data.get('duration', 5.0)
    if not isinstance(speed, (int, float)) or speed < 1 or speed > 100:
        errors['speed'] = "speed must be between 1 and 100"
    if not isinstance(duration, (int, float)) or duration <= 0:
        errors['duration'] = "duration must be a positive number"
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        success = use_rotary_tool(
            speed=speed,
            duration=duration
        )
        if success:
            return Response({"status": "rotary tool operation completed"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to use rotary tool"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def soil_sensor_view(request):
    """Get soil sensor readings"""
    try:
        readings = read_soil_sensor()
        if readings is None:
            return Response({"error": "Could not read soil sensor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = SoilSensorSerializer(readings)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def weeder_view(request):
    """Use the weeder tool to remove weeds at a specific location"""
    serializer = WeederSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    errors = {}
    for axis in ['x', 'y', 'z']:
        if not isinstance(data.get(axis), (int, float)):
            errors[axis] = f"{axis} must be a number"
    working_depth = data.get('working_depth', -20)
    speed = data.get('speed', 100)
    if not isinstance(working_depth, (int, float)):
        errors['working_depth'] = "working_depth must be a number"
    if not isinstance(speed, (int, float)) or speed < 1 or speed > 100:
        errors['speed'] = "speed must be between 1 and 100"
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        success = use_weeder(
            x=data['x'],
            y=data['y'],
            z=data['z'],
            working_depth=working_depth,
            speed=speed
        )
        if success:
            return Response({"status": "weeding completed successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to complete weeding operation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)