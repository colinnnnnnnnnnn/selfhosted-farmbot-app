from django.urls import path
from .views import (
    connect_view, move_absolute_view, move_relative_view,
    emergency_lock_view, emergency_unlock_view, find_home_view,
    go_to_home_view, power_off_view, reboot_view, servo_angle_view,
    lua_script_view, get_position_view, send_message_view, take_photo_view,
    get_latest_photo_view, clear_photos_view, register_view, login_view, logout_view, me_view,
    social_auth_callback
)

urlpatterns = [
    path('auth/register/', register_view, name='auth-register'),
    path('auth/login/', login_view, name='auth-login'),
    path('auth/logout/', logout_view, name='auth-logout'),
    path('auth/me/', me_view, name='auth-me'),
    path('auth/social-callback/', social_auth_callback, name='auth-social-callback'),

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
    path('get-latest-photo/', get_latest_photo_view, name='get-latest-photo'),
    path('clear-photos/', clear_photos_view, name='clear-photos'),
]