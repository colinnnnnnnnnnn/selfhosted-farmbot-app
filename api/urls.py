from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SequenceViewSet,
    connect_view, move_absolute_view, move_relative_view,
    emergency_lock_view, emergency_unlock_view, find_home_view,
    go_to_home_view, power_off_view, reboot_view, servo_angle_view,
    lua_script_view, get_position_view, send_message_view, take_photo_view,
    register_view, login_view, logout_view, me_view, water_plant_view,
    mount_tool_view, dismount_tool_view, dispense_view, clear_photos_view
)

router = DefaultRouter()
router.register(r'sequences', SequenceViewSet, basename='sequence')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', register_view, name='auth-register'),
    path('auth/login/', login_view, name='auth-login'),
    path('auth/logout/', logout_view, name='auth-logout'),
    path('auth/me/', me_view, name='auth-me'),
    path('auth/', include('allauth.urls')),

    path('connect/', connect_view, name='connect'),
    path('move-absolute/', move_absolute_view, name='move-absolute'),
    path('move-relative/', move_relative_view, name='move-relative'),
    path('emergency-lock/', emergency_lock_view, name='emergency-lock'),
    path('emergency-unlock/', emergency_unlock_view, name='emergency-unlock'),
    path('find-home/', find_home_view, name='find-home'),
    path('go-to-home/', go_to_home_view, name='go-to-home'),
    path('power-off/', power_off_view, name='power-off'),
    path('reboot/', reboot_view, name='reboot'),
    path('servo-angle/', servo_angle_view, name='servo-angle'),
    path('lua-script/', lua_script_view, name='lua-script'),
    path('position/', get_position_view, name='position'),
    path('send-message/', send_message_view, name='send-message'),
    path('take-photo/', take_photo_view, name='take-photo'),
    # Backwards-compatible alias used by the frontend
    path('get-latest-photo/', take_photo_view, name='get_latest_photo'),
    path('clear-photos/', clear_photos_view, name='clear-photos'),
    path('water-plant/', water_plant_view, name='water-plant'),
    path('mount-tool/', mount_tool_view, name='mount-tool'),
    path('dismount-tool/', dismount_tool_view, name='dismount-tool'),
    path('dispense/', dispense_view, name='dispense'),
]