"""
Tests for API serialization validation.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class ValidationTestCase(TestCase):
    """Test API request validation and error messages"""

    def setUp(self):
        self.client = APIClient()

    # Position/Coordinate Tests
    def test_position_valid(self):
        """Test valid position coordinates"""
        response = self.client.post('/api/move-absolute/', {
            'x': 100,
            'y': 200,
            'z': -50,
            'speed': 100
        })
        # Should not return validation error (may fail for other reasons)
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_position_x_out_of_bounds(self):
        """Test X coordinate out of bounds"""
        response = self.client.post('/api/move-absolute/', {
            'x': 5000,  # Max is 3000
            'y': 200,
            'z': -50
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('x', response.data)

    def test_position_z_out_of_bounds(self):
        """Test Z coordinate out of bounds (too deep)"""
        response = self.client.post('/api/move-absolute/', {
            'x': 100,
            'y': 200,
            'z': -500  # Min is -400
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('z', response.data)

    def test_position_invalid_type(self):
        """Test invalid data type for coordinates"""
        response = self.client.post('/api/move-absolute/', {
            'x': 'invalid',
            'y': 200,
            'z': -50
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Speed Tests
    def test_speed_valid(self):
        """Test valid speed values"""
        response = self.client.post('/api/move-absolute/', {
            'x': 100,
            'y': 200,
            'z': -50,
            'speed': 50
        })
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_speed_too_high(self):
        """Test speed exceeds maximum"""
        response = self.client.post('/api/move-absolute/', {
            'x': 100,
            'y': 200,
            'z': -50,
            'speed': 150  # Max is 100
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('speed', response.data)

    def test_speed_negative(self):
        """Test negative speed"""
        response = self.client.post('/api/move-absolute/', {
            'x': 100,
            'y': 200,
            'z': -50,
            'speed': -10
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Servo Angle Tests
    def test_servo_angle_valid(self):
        """Test valid servo angle"""
        response = self.client.post('/api/servo-angle/', {
            'pin': 11,
            'angle': 90
        })
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_servo_angle_invalid_pin(self):
        """Test invalid GPIO pin"""
        response = self.client.post('/api/servo-angle/', {
            'pin': 999,  # Invalid pin
            'angle': 90
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('pin', response.data)

    def test_servo_angle_out_of_range(self):
        """Test servo angle out of range"""
        response = self.client.post('/api/servo-angle/', {
            'pin': 11,
            'angle': 270  # Max is 180
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('angle', response.data)

    # Volume/Dispensing Tests
    def test_dispense_valid(self):
        """Test valid dispensing parameters"""
        response = self.client.post('/api/dispense/', {
            'milliliters': 100,
            'pin': 8
        })
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dispense_volume_too_small(self):
        """Test volume below minimum"""
        response = self.client.post('/api/dispense/', {
            'milliliters': 0.001,  # Min is 0.01
            'pin': 8
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('milliliters', response.data)

    def test_dispense_volume_too_large(self):
        """Test volume exceeds maximum"""
        response = self.client.post('/api/dispense/', {
            'milliliters': 10000,  # Max is 5000
            'pin': 8
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('milliliters', response.data)

    def test_dispense_missing_pin_and_tool(self):
        """Test dispensing without pin or tool_name"""
        response = self.client.post('/api/dispense/', {
            'milliliters': 100
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Seed Injector Tests
    def test_seed_injector_valid(self):
        """Test valid seed injection parameters"""
        response = self.client.post('/api/seed-injector/', {
            'seeds_count': 10,
            'dispense_time': 2.0
        })
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_seed_count_zero(self):
        """Test seed count of zero"""
        response = self.client.post('/api/seed-injector/', {
            'seeds_count': 0,
            'dispense_time': 1.0
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_seed_count_too_large(self):
        """Test seed count exceeds maximum"""
        response = self.client.post('/api/seed-injector/', {
            'seeds_count': 20000,  # Max is 10000
            'dispense_time': 1.0
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Rotary Tool Tests
    def test_rotary_tool_valid(self):
        """Test valid rotary tool parameters"""
        response = self.client.post('/api/rotary-tool/', {
            'speed': 75,
            'duration': 10.0
        })
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rotary_tool_duration_too_short(self):
        """Test duration below minimum"""
        response = self.client.post('/api/rotary-tool/', {
            'speed': 100,
            'duration': 0.01  # Min is 0.1
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rotary_tool_duration_too_long(self):
        """Test duration exceeds maximum"""
        response = self.client.post('/api/rotary-tool/', {
            'speed': 100,
            'duration': 4000  # Max is 3600
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Weeder Tests
    def test_weeder_valid(self):
        """Test valid weeding parameters"""
        response = self.client.post('/api/weeder/', {
            'x': 100,
            'y': 200,
            'z': -50,
            'working_depth': -20,
            'speed': 100
        })
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weeder_depth_positive(self):
        """Test weeding depth should be negative"""
        response = self.client.post('/api/weeder/', {
            'x': 100,
            'y': 200,
            'z': -50,
            'working_depth': 20  # Should be negative
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weeder_depth_too_deep(self):
        """Test weeding depth exceeds maximum"""
        response = self.client.post('/api/weeder/', {
            'x': 100,
            'y': 200,
            'z': -50,
            'working_depth': -300  # Max depth is -200
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Lua Script Tests
    def test_lua_script_valid(self):
        """Test valid Lua script"""
        response = self.client.post('/api/lua-script/', {
            'lua_string': 'send_message("Hello from Lua")'
        })
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lua_script_empty(self):
        """Test empty Lua script"""
        response = self.client.post('/api/lua-script/', {
            'lua_string': ''
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lua_script_forbidden_command(self):
        """Test Lua script with forbidden commands"""
        response = self.client.post('/api/lua-script/', {
            'lua_string': 'os.execute("rm -rf /")'  # Forbidden
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('os.execute', str(response.data))

    def test_lua_script_too_long(self):
        """Test Lua script exceeds max length"""
        response = self.client.post('/api/lua-script/', {
            'lua_string': 'x = 1\n' * 2000  # Create large script
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ErrorMessageTestCase(TestCase):
    """Test that error messages are helpful and specific"""

    def setUp(self):
        self.client = APIClient()

    def test_error_message_includes_bounds(self):
        """Test that error message includes valid bounds"""
        response = self.client.post('/api/move-absolute/', {
            'x': 5000,
            'y': 200,
            'z': -50
        })
        error_msg = str(response.data.get('x', []))
        self.assertIn('3000', error_msg)  # Should show max value

    def test_error_message_includes_actual_value(self):
        """Test that error message shows the invalid value provided"""
        response = self.client.post('/api/servo-angle/', {
            'pin': 11,
            'angle': 270
        })
        error_msg = str(response.data.get('angle', []))
        self.assertIn('270', error_msg)  # Should show provided value

    def test_error_message_helpful_for_missing_field(self):
        """Test error message for missing required field"""
        response = self.client.post('/api/move-absolute/', {
            'x': 100,
            'y': 200
            # Missing z
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('z', response.data)
