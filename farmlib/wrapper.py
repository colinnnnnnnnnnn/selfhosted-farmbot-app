from farmlib.farmbot import Farmbot
import threading
import time
import requests
import io
import os
import re
import math
from dotenv import load_dotenv
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

load_dotenv()

# Global variables
bot = None
bot_token = None
api_server = None
connection_event = threading.Event()
photo_event = threading.Event()
photo_data = {'url': None}

def get_photo_counter():
    """Получить текущий номер фотографии из файла"""
    counter_file = os.path.join(os.path.dirname(__file__), 'photo_counter.txt')
    try:
        with open(counter_file, 'r') as f:
            return int(f.read().strip())
    except:
        return 1

def increment_photo_counter():
    """Увеличить и сохранить номер фотографии"""
    counter_file = os.path.join(os.path.dirname(__file__), 'photo_counter.txt')
    counter = get_photo_counter() + 1
    with open(counter_file, 'w') as f:
        f.write(str(counter))
    return counter

class ConnectHandler:
    def on_connect(self, bot, client):
        print("Connected to FarmBot!")
        connection_event.set()

    def on_change(self, bot, state):
        print("State updated")

    def on_log(self, bot, log):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'logs',
            {
                'type': 'log_message',
                'message': log
            }
        )
        if isinstance(log, dict):
            # Проверяем сообщение о загрузке фото
            message = log.get('message', '')
            if 'Uploaded image:' in message:
                # 1) Пытаемся извлечь полный URL из текста лога
                match = re.search(r"(https?://[^\s]+/rails/active_storage/blobs/redirect/[^\s]+/image_\d+)", message)
                if match:
                    photo_data['url'] = match.group(1)
                    print(f"Photo URL: {photo_data['url']}")
                    photo_event.set()
                    return

                # 2) Если в сообщении прямой ссылки нет, запрашиваем последнюю картинку из API
                try:
                    if api_server and bot_token:
                        resp = requests.get(
                            f"{api_server}/api/images",
                            headers={"Authorization": f"Bearer {bot_token}"},
                            timeout=10
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            # Берем последний элемент (обычно самое новое изображение)
                            if isinstance(data, list) and len(data) > 0:
                                last = data[-1]
                                url = last.get('attachment_url') or last.get('url')
                                if url:
                                    photo_data['url'] = url
                                    print(f"Photo URL: {photo_data['url']}")
                                    photo_event.set()
                                    return
                except Exception as e:
                    print(f"Failed to fetch latest image URL from API: {e}")

    def on_error(self, bot, response):
        print("Error:", response.errors)

    def on_response(self, bot, response):
        print("Response:", response.id)

def connect_bot():
    """Connect to FarmBot in a separate thread"""
    global bot, bot_token, api_server
    if bot is not None:
        return True
    connection_event.clear()
    photo_event.clear()
    photo_data['url'] = None
    try:
        api_server = "http://144.21.63.33:3000"
        bot = Farmbot.login(
            email=os.getenv('FARMBOT_EMAIL'),
            password=os.getenv('FARMBOT_PASSWORD'),
            server=api_server
        )
        bot_token = bot.password
        handler = ConnectHandler()
        bot.handler = handler
        connection_thread = threading.Thread(target=lambda: bot.connect(handler))
        connection_thread.daemon = True
        connection_thread.start()
        if not connection_event.wait(timeout=10):
            print("Failed to connect to FarmBot")
            bot = None
            bot_token = None
            return False
        return True
    except Exception as e:
        print(f"Failed to connect: {e}")
        bot = None
        bot_token = None
        return False

def move_absolute(x, y, z, speed=100):
    """Simple move function that can be called from anywhere"""
    if bot is None:
        print("Bot not connected!")
        return False

    try:
        print(f"Moving to ({x}, {y}, {z}) at {speed}% speed")
        return bot.move_absolute(x, y, z, speed)
    except Exception as e:
        print(f"Error in move_absolute: {e}")
        return False


def emergency_lock():
    """Trigger emergency lock on the global bot."""
    global bot
    if bot is None:
        print("Couldn't lock")
        return False

    try:
        print("Emergency Lock!")
        return bot.emergency_lock()
    except Exception as e:
        print(f"Error in emergency_lock: {e}")
        return False

def emergency_unlock():
    """Trigger emergency unlock on the global bot."""
    global bot
    if bot is None:
        print("Couldn't unlock")
        return False

    try:
        print("Emergency Unlock!")
        return bot.emergency_unlock()
    except Exception as e:
        print(f"Error in emergency_unlock: {e}")
        return False

def find_home():
    """Command the global bot to find its home position."""
    global bot
    if bot is None:
        print("Couldn't find home")
        return False

    try:
        print("Finding Home!(Initial position)")
        return bot.find_home()
    except Exception as e:
        print(f"Error in find_home: {e}")
        return False


def go_to_home():
    """Move the global bot to its home position."""
    global bot
    if bot is None:
        print("Couldn't go to home")
        return False

    try:
        print("Going to Home!(0,0,0)")
        return bot.go_to_home()
    except Exception as e:
        print(f"Error in go_to_home: {e}")
        return False

def move_relative(x, y, z, speed=100):
    if bot is None:
        print("Bot not connected!")
        return False
    try:
        print(f"Moving relative by ({x}, {y}, {z}) at {speed}% speed")
        return bot.move_relative(x, y, z, speed)
    except Exception as e:
        print(f"Error in move_relative: {e}")
        return False

def power_off():
    if bot is None:
        print("Bot not connected!")
        return False
    try:
        print("Powering off")
        return bot.power_off()
    except Exception as e:
        print(f"Error in power_off: {e}")
        return False

def reboot():
    if bot is None:
        print("Bot not connected!")
        return False
    try:
        print("Rebooting")
        return bot.reboot()
    except Exception as e:
        print(f"Error in reboot: {e}")
        return False

def servo_angle(pin, angle):
    if bot is None:
        print("Bot not connected!")
        return False
    try:
        print(f"Setting servo on pin {pin} to angle {angle}")
        return bot.set_servo_angle(pin, angle)
    except Exception as e:
        print(f"Error in servo_angle: {e}")
        return False


def lua_script(lua_string):
    if bot is None:
        print("Bot not connected!")
        return False
    try:
        print(f"Executing Lua script: {lua_string}")
        return bot.lua(lua_string)
    except Exception as e:
        print(f"Error in lua_script: {e}")
        return False


def get_position():
    """Get current bot position"""
    if bot is None:
        print("Bot not connected!")
        return None
    return bot.position()

def send_message(message):
    """Send a message to the bot"""
    if bot is None:
        print("Bot not connected!")
        return
    try:
        return bot.send_message(message)
    except Exception as e:
        print(f"Error in send_message: {e}")
        return False

def verify_tool():
    """
    Verifies if a tool is properly attached to the UTM.
    Returns:
        bool: True if tool is detected, False otherwise
    """
    if bot is None:
        print("Bot not connected!")
        return False
    
    try:
        # The verify_tool() function in Lua checks the electrical connection
        lua_code = "return verify_tool()"
        result = bot.lua(lua_code)
        return bool(result)
    except Exception as e:
        print(f"Error verifying tool: {e}")
        return False

def mount_tool(tool_name):
    """
    Mounts the given tool using Lua script.
    Args:
        tool_name (str): Name of the tool to mount
    Returns:
        bool: True if mounting was successful, False otherwise
    """
    if bot is None:
        print("Bot not connected!")
        return False
    
    try:
        # First, check if the tool exists in the tools list
        lua_code = f"""
            tools = api({{"url" = "/api/tools/"}})
            tool_found = false
            for _, tool in ipairs(tools) do
                if tool.name == "{tool_name}" then
                    tool_found = true
                    break
                end
            end
            return tool_found
        """
        tool_exists = bot.lua(lua_code)
        
        if not tool_exists:
            print(f"Tool '{tool_name}' not found in tools database")
            return False
            
        print(f"Mounting {tool_name} tool...")
        lua_code = f"mount_tool(\"{tool_name}\")"
        bot.lua(lua_code)
        
        # Verify tool was mounted successfully
        if not verify_tool():
            print("Tool mount verification failed - no electrical connection detected")
            return False
            
        return True
    except Exception as e:
        print(f"Error mounting tool: {e}")
        return False

def dismount_tool():
    """
    Dismounts the currently mounted tool using Lua script.
    Returns:
        bool: True if dismounting was successful, False otherwise
    """
    if bot is None:
        print("Bot not connected!")
        return False
    
    try:
        # Check if there's actually a tool mounted
        if not verify_tool():
            print("No tool detected - nothing to dismount")
            return True
            
        print("Dismounting tool...")
        lua_code = "dismount_tool()"
        bot.lua(lua_code)
        
        # Verify tool was actually dismounted
        if verify_tool():
            print("Tool still detected after dismount attempt")
            return False
            
        return True
    except Exception as e:
        print(f"Error dismounting tool: {e}")
        return False

def _water_dispense_params(tool_name=None, pin=None):
    """Helper function to format water/dispense parameters for Lua code"""
    params = ""
    if tool_name is not None:
        params += ", {"
        params += f"tool_name = \"{tool_name}\""
    if pin is not None:
        params += ", " if tool_name is None else ", "
        params += "{"if tool_name is None else ""
        params += f"pin = {pin}"
    if tool_name is not None or pin is not None:
        params += "})"
    else:
        params += ")"
    return params

def water_plant(x=6, y=600, z=-340):
    """
    Move to a position and water using pin control.
    Args:
        x (int): X coordinate for watering position. Default is water nozzle position.
        y (int): Y coordinate for watering position. Default is water nozzle position.
        z (int): Z coordinate for watering position. Default is water nozzle position.
    Returns:
        bool: True if watering was successful, False otherwise
    """
    if bot is None:
        print("Bot not connected!")
        return False
    
    WATER_PIN = 8  # Water pin number
    try:
        # First get current position
        current_pos = get_position()
        if current_pos is None:
            bot.send_message("Could not get current position", "error")
            return False

        bot.send_message(f"Starting watering sequence from {current_pos}")
        bot.send_message(f"Moving to watering position ({x}, {y}, {z})")
        
        # Move to safe height first to avoid collisions
        safe_z = max(current_pos[2], z, -200)  # Use highest Z of current, target, or -200
        bot.send_message(f"Moving up to safe height {safe_z}")
        bot.move_absolute(current_pos[0], current_pos[1], safe_z)
        time.sleep(2)  # Wait for Z movement
        
        # Move to X,Y position while at safe height
        bot.send_message(f"Moving to target X,Y position at safe height")
        bot.move_absolute(x, y, safe_z)
        time.sleep(3)  # Wait for XY movement
        
        # Finally move down to target Z
        bot.send_message(f"Moving down to target height {z}")
        bot.move_absolute(x, y, z)
        time.sleep(2)  # Wait for Z movement
        
        # Start watering
        bot.send_message("Activating water pump")
        bot.write_pin(pin_number=WATER_PIN, pin_value=1, pin_mode="digital")
        time.sleep(5)  # Water for 5 seconds
        bot.write_pin(pin_number=WATER_PIN, pin_value=0, pin_mode="digital")
        bot.send_message("Water pump deactivated")
        
        bot.send_message("Watering sequence completed successfully")
        return True
        
    except Exception as e:
        print(f"Error during watering: {e}")
        # Safety: ensure water is off
        try:
            bot.write_pin(pin_number=WATER_PIN, pin_value=0, pin_mode="digital")
        except:
            pass
        return False

def dispense(milliliters, tool_name=None, pin=None):
    """
    Dispense a specific amount of liquid.
    Args:
        milliliters (float): Amount of liquid to dispense in milliliters
        tool_name (str, optional): Name of the dispensing tool to use
        pin (int, optional): Specific pin number to control for dispensing
    Returns:
        bool: True if dispensing was successful, False otherwise
    """
    if bot is None:
        print("Bot not connected!")
        return False
    
    try:
        print(f"Dispensing {milliliters}ml...")
        lua_code = f"dispense({milliliters}{_water_dispense_params(tool_name, pin)})"
        bot.lua(lua_code)
        return True
    except Exception as e:
        print(f"Error dispensing: {e}")
        return False

def take_photo():
    """Take a photo and get the most recent photo from the FarmBot Web App."""
    if bot is None or not connection_event.is_set():
        if not connect_bot():
            print("Bot not connected!")
            return None

    try:
        # Trigger camera capture
        bot.take_photo()

        # Give the server time to process the photo
        time.sleep(10)

        # Get the most recent photo from the API
        latest_url = None
        for _ in range(30):  # ~30s timeout
            try:
                if api_server and bot_token:
                    # Get all images and sort by ID to get the most recent one
                    resp = requests.get(
                        f"{api_server}/api/images",
                        headers={"Authorization": f"Bearer {bot_token}"},
                        timeout=10
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if isinstance(data, list) and len(data) > 0:
                            # Sort by ID in descending order and get the first one
                            latest_image = sorted(data, key=lambda x: x.get('id', 0), reverse=True)[0]
                            image_id = latest_image.get('id')
                            url = latest_image.get('attachment_url') or latest_image.get('url')
                            if url:
                                latest_url = url
                                break
            except Exception as e:
                print(f"Error fetching latest image: {e}")
            time.sleep(1)

        if not latest_url:
            print("Timeout waiting for latest image")
            return None

        # Download the image from its signed URL
        response = requests.get(latest_url, headers={
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        })
        if response.status_code == 200 and response.headers.get('Content-Type', '').startswith('image/'):
            os.makedirs('farm_images', exist_ok=True)
            image_path = os.path.join('farm_images', f'image_{image_id}.jpg')
            with open(image_path, 'wb') as f:
                f.write(response.content)
            print(f"Image saved to {image_path}")

            # Increment persisted counter after successful save
            increment_photo_counter()

            return {
                'image': response.content,
                'content_type': 'image/jpeg',
                'id': image_id
            }
        else:
            print(f"Failed to download image: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error taking photo: {e}")
        return None

def read_soil_sensor():
    """
    Read the soil sensor data (moisture, temperature, etc.).
    Returns:
        dict: Dictionary containing soil sensor readings or None if failed
    """
    if bot is None:
        print("Bot not connected!")
        return None
    
    try:
        # Use pin 59 for soil sensor readings (standard pin for soil sensor)
        SOIL_SENSOR_PIN = 59
        
        # Read analog value from soil sensor
        bot.read_pin(pin_number=SOIL_SENSOR_PIN, pin_mode="analog")
        
        # Get the moisture value from pin reading (0-1023 range)
        moisture_raw = bot.state["pins"].get(str(SOIL_SENSOR_PIN), {}).get("value", 0)
        
        # Convert to percentage (0-100%)
        moisture_percent = (moisture_raw / 1023) * 100
        
        return {
            "moisture": round(moisture_percent, 2),
            "raw_value": moisture_raw
        }
    except Exception as e:
        print(f"Error reading soil sensor: {e}")
        return None

def use_seed_injector(seeds_count=1, dispense_time=1.0):
    """
    Use the seed injector to plant a specific number of seeds.
    Args:S
        seeds_count (int): Number of seeds to plant
        dispense_time (float): Time in seconds for each seed dispensing action
    Returns:
        bool: True if successful, False otherwise
    """
    if bot is None:
        print("Bot not connected!")
        return False
    
    try:
        # First ensure we have the seed injector mounted
        if not verify_tool() or not mount_tool("seed_injector"):
            print("Failed to mount seed injector")
            return False
            
        # PIN 10 is typically used for seed injection
        SEED_PIN = 10
        
        print(f"Dispensing {seeds_count} seeds...")
        
        for i in range(seeds_count):
            # Activate seed injector
            bot.write_pin(pin_number=SEED_PIN, pin_value=1, pin_mode="digital")
            time.sleep(dispense_time)  # Wait for seed to drop
            bot.write_pin(pin_number=SEED_PIN, pin_value=0, pin_mode="digital")
            
            if i < seeds_count - 1:  # Don't wait after the last seed
                time.sleep(0.5)  # Short pause between seeds
        
        return True
    except Exception as e:
        print(f"Error using seed injector: {e}")
        # Safety: ensure pin is off
        try:
            bot.write_pin(pin_number=SEED_PIN, pin_value=0, pin_mode="digital")
        except:
            pass
        return False

def use_rotary_tool(speed=100, duration=5.0):
    """
    Activate the rotary tool for operations like weeding or soil working.
    Args:
        speed (int): Speed percentage for the rotary tool (0-100)
        duration (float): How long to run the tool in seconds
    Returns:
        bool: True if successful, False otherwise
    """
    if bot is None:
        print("Bot not connected!")
        return False
    
    try:
        # First ensure we have the rotary tool mounted
        if not verify_tool() or not mount_tool("rotary_tool"):
            print("Failed to mount rotary tool")
            return False
            
        # PIN 11 is typically used for rotary tool control
        ROTARY_TOOL_PIN = 11
        
        # Convert speed percentage to pin value (0-255 for analog)
        pin_value = int((speed / 100) * 255)
        
        print(f"Activating rotary tool at {speed}% speed...")
        
        # Activate rotary tool
        bot.write_pin(pin_number=ROTARY_TOOL_PIN, pin_value=pin_value, pin_mode="analog")
        time.sleep(duration)
        
        # Turn off tool
        bot.write_pin(pin_number=ROTARY_TOOL_PIN, pin_value=0, pin_mode="analog")
        
        return True
    except Exception as e:
        print(f"Error using rotary tool: {e}")
        # Safety: ensure pin is off
        try:
            bot.write_pin(pin_number=ROTARY_TOOL_PIN, pin_value=0, pin_mode="analog")
        except:
            pass
        return False

def use_weeder(x, y, z, working_depth=-20, speed=100):
    """
    Use the weeder tool to remove weeds at a specific location.
    Args:
        x (float): X coordinate for weeding
        y (float): Y coordinate for weeding
        z (float): Z coordinate approach height
        working_depth (float): How deep to insert the weeder tool (negative number, default -20mm)
        speed (int): Speed percentage for the rotary tool (0-100)
    Returns:
        bool: True if successful, False otherwise
    """
    if bot is None:
        print("Bot not connected!")
        return False
    
    try:
        # First ensure we have the weeder tool mounted
        if not verify_tool() or not mount_tool("weeder"):
            print("Failed to mount weeder")
            return False

        # Get current position
        current_pos = get_position()
        if current_pos is None:
            bot.send_message("Could not get current position", "error")
            return False

        bot.send_message(f"Starting weeding sequence at ({x}, {y})")
        
        # Move to safe height first
        safe_z = max(current_pos[2], z, -100)  # Use highest Z of current, target, or -100
        bot.send_message(f"Moving to safe height {safe_z}")
        bot.move_absolute(current_pos[0], current_pos[1], safe_z)
        time.sleep(2)  # Wait for Z movement
        
        # Move to target X,Y at safe height
        bot.send_message(f"Moving to target position at safe height")
        bot.move_absolute(x, y, safe_z)
        time.sleep(3)  # Wait for XY movement
        
        # Start rotary tool before inserting
        bot.send_message("Activating weeder tool")
        WEEDER_PIN = 11  # Weeder uses the same pin as rotary tool
        pin_value = int((speed / 100) * 255)
        bot.write_pin(pin_number=WEEDER_PIN, pin_value=pin_value, pin_mode="analog")
        time.sleep(1)  # Let tool spin up
        
        # Move down to working depth
        bot.send_message(f"Lowering tool to working depth {working_depth}")
        final_z = z + working_depth
        bot.move_absolute(x, y, final_z)
        time.sleep(3)  # Allow time for weeding action
        
        # Small circular movement to ensure weed removal
        radius = 5  # 5mm radius
        bot.send_message("Performing weeding pattern")
        for angle in [0, 90, 180, 270]:  # 4-point circle
            rad = math.radians(angle)
            dx = radius * math.cos(rad)
            dy = radius * math.sin(rad)
            bot.move_absolute(x + dx, y + dy, final_z)
            time.sleep(1)
        
        # Return to center
        bot.move_absolute(x, y, final_z)
        time.sleep(1)
        
        # Move back up to safe height
        bot.send_message("Moving back to safe height")
        bot.move_absolute(x, y, safe_z)
        time.sleep(2)
        
        # Turn off tool
        bot.write_pin(pin_number=WEEDER_PIN, pin_value=0, pin_mode="analog")
        bot.send_message("Weeding sequence completed")
        
        return True
        
    except Exception as e:
        print(f"Error using weeder: {e}")
        # Safety: ensure tool is off
        try:
            bot.write_pin(pin_number=11, pin_value=0, pin_mode="analog")
        except:
            pass
        return False

def main():
    # Start connection in background thread
    connection_thread = threading.Thread(target=connect_bot)
    connection_thread.daemon = True
    connection_thread.start()

    # Wait a moment for connection
    print("Connecting...")
    time.sleep(5)

    # Now you can use simple functions
    move_absolute(0, 100, 10)
    time.sleep(2)

    position = get_position()
    print(f"Current position: {position}")

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()
