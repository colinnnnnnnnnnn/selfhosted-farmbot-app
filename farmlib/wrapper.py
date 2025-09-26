from farmlib.farmbot import Farmbot
import threading
import time
import requests
import io
import os
from dotenv import load_dotenv
import re

# Load .env for configuration
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
        api_server = os.getenv("FARM_BOT_SERVER", "https://my.farm.bot")
        fb_email = os.getenv("FARM_BOT_EMAIL")
        fb_password = os.getenv("FARM_BOT_PASSWORD")
        if not fb_email or not fb_password:
            raise RuntimeError("Missing FARM_BOT_EMAIL or FARM_BOT_PASSWORD in environment")
        bot = Farmbot.login(
            email=fb_email,
            password=fb_password,
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
    """Simple absolute move."""
    if bot is None or not connection_event.is_set():
        if not connect_bot():
            print("Bot not connected!")
            return
    print(f"Moving to ({x}, {y}, {z}) at {speed}% speed")
    return bot.move_absolute(x, y, z, speed)


def emergency_lock():
    global bot
    if bot is None or not connection_event.is_set():
        if not connect_bot():
            print("Couldn't lock")
            return

    print("Emergency Lock!")
    return bot.emergency_lock()

def emergency_unlock():
    global bot
    if bot is None or not connection_event.is_set():
        if not connect_bot():
            print("Couldn't unlock")
            return

    print("Emergency Unlock!")
    return bot.emergency_unlock()

def find_home():
    global bot
    if bot is None or not connection_event.is_set():
        if not connect_bot():
            print("Couldn't find home")
            return

    print("Finding Home!(Initial position)")
    return bot.find_home()


def go_to_home():
    global bot
    if bot is None or not connection_event.is_set():
        if not connect_bot():
            print("Couldn't go to home")
            return

    print("Going to Home!(0,0,0)")
    return bot.go_to_home()

def move_relative(x, y, z, speed=100):
    if bot is None or not connection_event.is_set():
        if not connect_bot():
            print("Bot not connected!")
            return
    print(f"Moving relative by ({x}, {y}, {z}) at {speed}% speed")
    return bot.move_relative(x, y, z, speed)

def power_off():
    if bot is None or not connection_event.is_set():
        if not connect_bot():
            print("Bot not connected!")
            return
    print("Powering off")
    return bot.power_off()

def reboot():
    if bot is None or not connection_event.is_set():
        if not connect_bot():
            print("Bot not connected!")
            return
    print("Rebooting")
    return bot.reboot()

def servo_angle(pin, angle):
    if bot is None or not connection_event.is_set():
        if not connect_bot():
            print("Bot not connected!")
            return
    print(f"Setting servo on pin {pin} to angle {angle}")
    return bot.set_servo_angle(pin, angle)


def lua_script(lua_string):
    if bot is None or not connection_event.is_set():
        if not connect_bot():
            print("Bot not connected!")
            return
    print(f"Executing Lua script: {lua_string}")
    return bot.lua(lua_string)


def get_position():
    """Get current bot position"""
    if bot is None or not connection_event.is_set():
        if not connect_bot():
            print("Bot not connected!")
            return None
    try:
        return bot.position()
    except Exception:
        return None

def send_message(message):
    """Send a message to the bot"""
    if bot is None or not connection_event.is_set():
        if not connect_bot():
            print("Bot not connected!")
            return
    return bot.send_message(message)

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
