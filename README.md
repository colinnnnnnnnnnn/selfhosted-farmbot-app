# Self-Hosted FarmBot Web App


## Getting Started

### Configuration

1.  Clone the repository.
2.  Create a `.env` file from the template: `cp .env.example .env`
3.  Fill in the required values in the `.env` file:
    *   `SECRET_KEY`: A new Django secret key. You can generate one easily.
    *   `FARMBOT_EMAIL` & `FARMBOT_PASSWORD`: Your FarmBot Web App credentials.
    *   `GOOGLE_OAUTH2_CLIENT_ID` & `GOOGLE_OAUTH2_CLIENT_SECRET`: For Google social login.
    *   `GITHUB_CLIENT_ID` & `GITHUB_CLIENT_SECRET`: For GitHub social login.

## Running the Application

You have two methods to run the application:

### Method 1: Locally

This method uses the `run.py` script to install all dependencies and start both the backend and frontend servers in your local environment.

```bash
python run.py
```

*   The backend API will be available at `http://localhost:8000`.
*   The frontend development server will be available at `http://localhost:3000`.

### Method 2: Docker

This is the recommended method for a consistent and isolated development environment. It runs the backend and frontend in separate containers.

```bash
docker-compose up --build
```

*   This command builds the images and starts the services.
*   Logs from both services will be streamed to your terminal.
*   Press `Ctrl+C` to stop the application.

## API Usage Examples

### Authentication (Get Token)

Use this command to log in with a user's email and password and receive an authentication token.(use username instead of email for user)

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
-H "Content-Type: application/json" \
-d '{
    "email": "your_email@example.com",
    "password": "your_password"
}'
```

### Creating a Sequence

Replace `YOUR_TOKEN_HERE` with the token obtained from logging in.

```bash
curl -X POST http://localhost:8000/api/sequences/ \
-H "Authorization: Token YOUR_TOKEN_HERE" \
-H "Content-Type: application/json" \
-d '{
    "name": "My First Sequence",
    "steps": [
        { "order": 0, "command": "move_absolute", "parameters": {"x": 50, "y": 50, "z": 0} },
        { "order": 1, "command": "take_photo", "parameters": {} }
    ]
}'
```

### Real-time Log Streaming

Use a command-line WebSocket client like `websocat` to connect to the log stream.

```bash
websocat ws://127.0.0.1:8000/ws/logs/
```