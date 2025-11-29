# FarmBot Web App Changelog

## November 2025

### Sequence Management & Execution
* Created `SequenceEditor.js` modal component with full CRUD operations for creating, editing, and deleting sequences.
* Implemented drag-to-reorder steps functionality for intuitive sequence management.
* Added support for 12 commands in sequences: move_absolute, move_relative, write_pin, read_pin, wait, send_message, find_home, take_photo, water, weed, inject_seed, and read_soil_sensor.
* Added sequence execute functionality with 10-second delays between steps for safe, controlled automation.
* Fixed `take_photo` command to create database records with coordinates and metadata, ensuring sequence-captured photos appear in gallery immediately.

---

### Photo Management & Frontend
* Implemented cursor-based pagination in `PhotoGallery.js` component for efficient browsing of large photo collections.
* Added "Load More" button to fetch additional photos from API with error handlers displaying placeholders on load failures.
* Added "Load to Grid" button to fetch and display photos on FarmBot map grid with automatic grid sync after sequence captures.
* Implemented photo grid sync feature that transforms API responses to grid-compatible format for seamless integration.

---

### UI & Layout Improvements
* Consolidated all action buttons (Water, Weed, Inject Seed, Read Soil, Rotary Tool) into `ActionButtons` component with integrated tool dropdown.
* Implemented Mount/Dismount functionality for tool management within the Actions section.
* Fixed top row spacing with `flex: 1` distribution for equal width containers and increased max height to 320px to accommodate all controls.

---

### Backend API & WebSocket
* Changed OAuth authentication from popup + postMessage flow to redirect flow for improved compatibility and security.
* Updated OAuth callback to redirect to `http://localhost:3000?auth_token=xxx` with `useAuth.js` hook reading tokens from URL parameters.
* Fixed `LogConsumer.disconnect()` method signature to properly accept `close_code` parameter and improved error handling in API endpoints and WebSocket consumers.

---

### Bug Fixes & Import Reorganization

* Fixed imports in `api/views.py` - reorganized all imports to top of file (was causing NameError on api_view decorator).
* Added missing `Step` model to `api/models.py` with proper relationships to Sequence model.
* Created migration for new Step model and other pending database models.
* Fixed circular import issues in serializers and views.

---

### Photo Pagination
* Implemented cursor-based pagination for photo list endpoint to efficiently handle large image libraries.
* Added `PhotoCursorPagination` class with configurable page size (default: 20, max: 100).
* Updated `PhotoViewSet.list()` to return paginated responses with `next`/`previous` cursors.

---

### API Request/Response Serialization Validation
* Created comprehensive validation system in `api/validators.py` with 9 specialized validators for coordinates, speed, depth, volume, pins, angles, scripts, time, and counts.
* Enhanced all 11 serializers with field-level and object-level validation, detailed docstrings explaining constraints, and clear error messages.
* All validation endpoints now provide clear, actionable error messages to API clients showing valid ranges and actual values provided.

---

### Audit Logging Feature
* Added `AuditLog` model to record user actions and events for security and compliance.
* Implemented API endpoint `/api/export-auditlog/` to export audit logs as CSV or plain text log file (`.log`).
* Usage: `/api/export-auditlog/?format=csv` or `/api/export-auditlog/?format=log`

---

### Notification Preferences & Email Summaries
* Added `NotificationPreference` model for user notification settings (enable/disable, report frequency).
* Created API endpoint `/api/notification-preferences/` (GET/PUT) for users to manage notification preferences.
* Implemented summary email utility for daily/weekly/monthly FarmBot activity reports.
* Configured SMTP/email settings via `.env` and `settings.py` for secure email delivery.

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