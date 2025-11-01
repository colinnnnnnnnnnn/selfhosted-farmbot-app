from farmlib.farmbot import Farmbot
import threading
import time
import requests
import io
import os
import re
from dotenv import load_dotenv

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
    """Take a photo, download it by integer ID, save and return it."""
    if bot is None or not connection_event.is_set():
        if not connect_bot():
            print("Bot not connected!")
            return None

    try:
        # Trigger camera capture
        bot.take_photo()

        # Give the server time to process the photo to avoid placeholder
        time.sleep(10)

        # Load current counter
        image_id = get_photo_counter()
        latest_url = None

        # Poll API until that specific image ID becomes available
        for _ in range(30):  # ~30s timeout
            try:
                if api_server and bot_token:
                    resp = requests.get(
                        f"{api_server}/api/images/{image_id}",
                        headers={"Authorization": f"Bearer {bot_token}"},
                        timeout=10
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        url = data.get('attachment_url') or data.get('url')
                        if url:
                            latest_url = url
                            break
            except Exception as e:
                print(f"Error fetching image {image_id}: {e}")
            time.sleep(1)

        if not latest_url:
            print(f"Timeout waiting for image {image_id}")
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
