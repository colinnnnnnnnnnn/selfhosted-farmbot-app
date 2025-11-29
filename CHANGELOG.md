# FarmBot Web App Changelog

## November 2025

### Frontend Features
* **Sequence Editor** - Full modal UI with drag-to-reorder, 12 commands support (move, pins, wait, message, home, photo, water, weed, seed, soil sensor), 10-second delay between steps
* **Tool implementations** - Add tool frontend implementations - soil sensor, rottary, inject seed
* **UI Reorganization** - Moved tool selector into ActionButtons, improved top row layout with equal-width containers

### Backend Features
* **Photo Pagination API** - Cursor-based pagination for `/api/photos/` endpoint (default: 20, max: 100 per page)
* **API Validation** - Comprehensive validation system with 9 validators, enhanced serializers, 30+ test cases
* **Audit Logging** - `AuditLog` model with CSV/log export via `/api/export-auditlog/`
* **Notification Preferences** - User notification settings with daily/weekly/monthly email summaries

---

## October 2025
### New tool functionalities:
* Implemented Watering Tool functionality (frontend & backend)
* Implemented Weeder Tool functionality (frontend & backend)
* Added support for the Rotary Tool (backend)
* Added Seed Injector capabilities (backend)
* Added Soil Sensor readings (backend)

### Other changes:
* Created a run script to quickly setup everything
* OAuth2 implementation (for logging in with Google or Github)
* Migrated to Daphne as default ASGI server
* Added Docker support with docker-compose
* Implemented WebSocket for live updates
* Added a photo gallery to conveniently view all photos
* Implemented sequence editor API
* Created the web app logo
* Updated the design in figma