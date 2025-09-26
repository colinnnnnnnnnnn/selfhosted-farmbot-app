from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from .serializers import PositionSerializer, ServoAngleSerializer, MessageSerializer, LuaScriptSerializer
from farmlib.wrapper import connect_bot, move_absolute, move_relative, emergency_lock, emergency_unlock
from farmlib.wrapper import find_home, go_to_home, power_off, reboot, servo_angle, lua_script, get_position, send_message, take_photo
from farmlib.wrapper import move_relative as fb_move_relative
import threading

# Initialize bot connection when server starts
connection_thread = threading.Thread(target=connect_bot)
connection_thread.daemon = True
connection_thread.start()

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def register_view(request):
    username = request.data.get('username') or request.data.get('email')
    email = request.data.get('email') or username
    password = request.data.get('password')
    if not username or not password:
        return Response({"error": "username/email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({"error": "username already exists"}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=username, email=email, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def login_view(request):
    username = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')
    if not username or not password:
        return Response({"error": "username/email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({"error": "invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def social_auth_callback(request):
    """Handle social authentication callback and return token"""
    if request.user.is_authenticated:
        token, _ = Token.objects.get_or_create(user=request.user)
        return render(request, 'social_auth_callback.html', {
            'token': token.key,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email
            }
        })
    else:
        return JsonResponse({'error': 'Authentication failed'}, status=401)

@api_view(['POST'])
def logout_view(request):
    try:
        Token.objects.filter(user=request.user).delete()
        return Response({"status": "logged out"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def me_view(request):
    user = request.user
    return Response({"id": user.id, "username": user.username, "email": user.email}, status=status.HTTP_200_OK)

@api_view(['POST'])
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
def move_absolute_view(request):
    """Move FarmBot to absolute position"""
    serializer = PositionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        data = serializer.validated_data
        move_absolute(data['x'], data['y'], data['z'], data.get('speed', 100))
        return Response({"status": "moving"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def move_relative_view(request):
    """Move FarmBot relative to current position"""
    serializer = PositionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        data = serializer.validated_data
        fb_move_relative(data['x'], data['y'], data['z'], data.get('speed', 100))
        return Response({"status": "moving"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
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
def go_to_home_view(request):
    """Go to home position"""
    try:
        go_to_home()
        return Response({"status": "moving to home"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def power_off_view(request):
    """Power off FarmBot"""
    try:
        power_off()
        return Response({"status": "powered off"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def reboot_view(request):
    """Reboot FarmBot"""
    try:
        reboot()
        return Response({"status": "rebooting"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def servo_angle_view(request):
    """Set servo angle"""
    serializer = ServoAngleSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        data = serializer.validated_data
        servo_angle(data['pin'], data['angle'])
        return Response({"status": "servo angle set"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
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
def get_position_view(request):
    """Get current position"""
    try:
        position = get_position()
        if position is None:
            return Response({"error": "Bot not connected"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(position, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
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

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def take_photo_view(request):
    """Take a photo using FarmBot's camera"""
    try:
        result = take_photo()
        if result is None:
            return Response({"error": "Could not take photo"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Проверяем формат ответа в URL-параметре
        response_format = request.query_params.get('format', 'image')
        
        if response_format == 'json':
            # Возвращаем только URL
            return Response({"url": result['url']}, status=status.HTTP_200_OK)
        else:
            # Возвращаем само изображение
            from django.http import HttpResponse
            return HttpResponse(
                result['image'],
                content_type=result['content_type']
            )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_latest_photo_view(request):
    """Get the latest photo from the farm_images folder"""
    import os
    import glob
    from django.http import HttpResponse
    
    try:
        # Get the farm_images directory path
        farm_images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'farm_images')
        
        # Find all image files
        image_patterns = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
        all_files = []
        
        for pattern in image_patterns:
            files = glob.glob(os.path.join(farm_images_dir, pattern))
            all_files.extend(files)
        
        if not all_files:
            return Response({"error": "No photos found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get the most recent file
        latest_file = max(all_files, key=os.path.getctime)
        
        # Read and return the file
        with open(latest_file, 'rb') as f:
            image_data = f.read()
        
        # Determine content type
        if latest_file.lower().endswith('.jpg') or latest_file.lower().endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif latest_file.lower().endswith('.png'):
            content_type = 'image/png'
        elif latest_file.lower().endswith('.gif'):
            content_type = 'image/gif'
        else:
            content_type = 'image/jpeg'  # default
        
        return HttpResponse(image_data, content_type=content_type)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
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
