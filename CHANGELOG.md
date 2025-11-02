# FarmBot Web App Changelog

## November 2025

### 2025-11-02

#### What's new

* Added support for the Rotary Tool
  * Speed control (0-100%)
  * Duration settings
  * Tool verification
  * Safety controls
  * API endpoint: `/api/rotary-tool/`

* Implemented Weeder Tool functionality
  * Configurable working depth
  * Precise positioning control
  * Automatic tool mounting
  * 4-point circular weeding pattern
  * API endpoint: `/api/weeder/`

* Added Seed Injector capabilities
  * Precise seed count control
  * Adjustable dispense timing
  * Position tracking
  * API endpoint: `/api/seed-injector/`

* Integrated Soil Sensor readings
  * Real-time moisture data
  * Raw and percentage values
  * JSON response format
  * API endpoint: `/api/soil-sensor/`

#### Developer updates

* **New Photo Gallery System**
  * RESTful API for photo management
  * Metadata storage in database
  * Coordinate tracking
  * Automatic thumbnail generation
  * WebSocket updates for real-time changes

* **Authentication Improvements**
  * OAuth2 implementation
  * Google OAuth support
  * GitHub OAuth support
  * Enhanced token management

* **Infrastructure Updates**
  * Migrated to Daphne as default ASGI server
  * Added Docker support with docker-compose
  * Implemented WebSocket for live updates
  * Enhanced async operation handling

#### API Examples

**Weeder Tool Operation**
```http
POST /api/weeder/
Content-Type: application/json

{
    "x": 100,
    "y": 200,
    "z": 0,
    "working_depth": -25,
    "speed": 90
}
```

**Soil Sensor Reading**
```http
GET /api/soil-sensor/
```
```json
{
    "moisture": 65.4,
    "raw_value": 669
}
```

**Photo Gallery API**
```http
GET /api/photos/
```
```json
{
    "photos": [
        {
            "id": 1,
            "url": "/farm_images/image_1.jpg",
            "created_at": "2025-11-02T14:30:00Z",
            "coordinates": {"x": 100, "y": 200, "z": 0}
        }
    ]
}
```