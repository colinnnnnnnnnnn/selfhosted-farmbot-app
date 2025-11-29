# FarmBot Web App Changelog

## November 2025


### Load Photos to Grid

#### Photo Grid Sync Feature
* Added "Load to Grid" button to fetch photos from API and display them on the FarmBot map grid.
* Implemented `loadPhotosFromAPI()` function in `photoService.js` that:
  - Fetches all photos from `/api/photos/` with pagination support
  - Transforms API response to grid-compatible format
  - Updates photo state and localStorage
* Photos taken via sequences now appear on grid after clicking "Load to Grid" (previously only visible in gallery after refresh).

---

### Sequence Editor Frontend

#### Full Sequence Editor UI
* Created `SequenceEditor.js` modal component with list and edit views.
* Implemented drag-to-reorder steps functionality.
* Added support for 12 commands: move_absolute, move_relative, write_pin, read_pin, wait, send_message, find_home, take_photo, water, weed, inject_seed, read_soil_sensor.
* Added sequence create, edit, delete, and execute functionality.
* Added 10-second delay between sequence steps during execution.
* Modal auto-closes after sequence execution completes.
* Fixed ESLint warnings with useCallback for loadSequences.

---

### Sequence Photos Database Fix

#### Backend Fix for Sequence Photos
* Fixed `take_photo` command in sequences not creating database records.
* Added `_take_photo_with_db_record()` wrapper in `api/views.py` to ensure photos are saved to DB with coordinates.
* Sequence-taken photos now appear in gallery (previously only saved to disk).

---

### UI Reorganization & Fixes

#### Tool Selector & Action Buttons
* Moved `ToolSelector` component into `ActionButtons` for better UI organization.
* All action buttons (Water, Weed, Inject Seed, Read Soil, Rotary Tool) now in one container.
* Tool dropdown with Mount/Dismount buttons integrated into Actions section.

#### Top Row Layout Fixes
* Fixed spacing between containers in top row - all containers now use `flex: 1` for equal width.
* Increased top row max height to 320px to accommodate all controls.

---

### Rotary Tool

#### Rotary Tool Functionality
* Added `activateRotaryTool()` service function in `actionService.js`.
* Added "Rotary Tool" button in ActionButtons component.
* Backend endpoint integration for rotary tool activation.

---

### OAuth Redirect Flow Fix

#### OAuth Authentication Fix
* Changed OAuth from popup + postMessage flow to redirect flow.
* Updated `social_auth_callback.html` to redirect to `http://localhost:3000?auth_token=xxx`.
* Updated `useAuth.js` hook to read token from URL parameters.
* Fixed cross-origin communication issues with OAuth popup.

---

### Photo Gallery Pagination

#### Frontend Photo Pagination
* Implemented cursor-based pagination in `PhotoGallery.js` component.
* Added "Load More" button to fetch additional photos from API.
* Added `onError` handlers for photo images to show placeholders on load failure.
* Fixed ESLint warnings with useCallback for fetchPhotos.

---

### Backend Fixes

#### API & WebSocket Fixes
* Fixed `SequenceViewSet` pagination error by adding `pagination_class = None`.
* Fixed `LogConsumer.disconnect()` method signature to accept `close_code` parameter.

---

### Bug Fixes & Import Reorganization

#### Critical Bug Fixes
* Fixed imports in `api/views.py` - reorganized all imports to top of file (was causing NameError on api_view decorator)
* Added missing `Step` model to `api/models.py` with proper relationships to Sequence model
* Created migration for new Step model and other pending database models
* Fixed circular import issues in serializers and views

---

### Photo Pagination

#### Photo Pagination
* Implemented cursor-based pagination for photo list endpoint to efficiently handle large image libraries.
* Added `PhotoCursorPagination` class with configurable page size (default: 20, max: 100).
* Updated `PhotoViewSet.list()` to return paginated responses with `next`/`previous` cursors.
* Added 7 comprehensive tests for pagination functionality (all passing).
* Created `PHOTO_PAGINATION.md` documentation with API usage examples and frontend integration guide.

---

### API Validation

#### API Request/Response Serialization Validation
* Created comprehensive validation system in `api/validators.py` with 9 specialized validators:
* Enhanced all 11 serializers with:
  - Field-level and object-level validation
  - Detailed docstrings explaining constraints
  - Clear error messages showing valid ranges and actual values provided
* Added 30+ validation test cases covering valid/invalid inputs, boundary conditions, and error quality.
* Created `API_VALIDATION.md` documentation with error examples and endpoint reference.
* All validation endpoints now provide clear, actionable error messages to API clients.

---

### Audit Logging Feature

* Added `AuditLog` model to record user actions and events for security and compliance.
* Implemented API endpoint `/api/export-auditlog/` to export audit logs as CSV or plain text log file (`.log`).
	- Usage: `/api/export-auditlog/?format=csv` or `/api/export-auditlog/?format=log`

---

### Notification Preferences & Email Summaries

* Added `NotificationPreference` model for user notification settings (enable/disable, report frequency).
* Created API endpoint `/api/notification-preferences/` (GET/PUT) for users to manage notification preferences.
* Implemented summary email utility and management command to send daily/weekly/monthly FarmBot activity reports to users.
* Configured SMTP/email settings via `.env` and `settings.py` for secure email delivery.
* Only users with notifications enabled and matching frequency receive summary emails.

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