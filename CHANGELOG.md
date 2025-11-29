# FarmBot Web App Changelog

## November 2025


### November 2025 - Bug Fixes & Import Reorganization

#### Critical Bug Fixes
* Fixed imports in `api/views.py` - reorganized all imports to top of file (was causing NameError on api_view decorator)
* Added missing `Step` model to `api/models.py` with proper relationships to Sequence model
* Created migration for new Step model and other pending database models
* Fixed circular import issues in serializers and views

---

### November 2025 - Photo Pagination

#### Photo Pagination
* Implemented cursor-based pagination for photo list endpoint to efficiently handle large image libraries.
* Added `PhotoCursorPagination` class with configurable page size (default: 20, max: 100).
* Updated `PhotoViewSet.list()` to return paginated responses with `next`/`previous` cursors.
* Added 7 comprehensive tests for pagination functionality (all passing).
* Created `PHOTO_PAGINATION.md` documentation with API usage examples and frontend integration guide.

---

### November 2025 - API Validation

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

### November 2025 - Audit Logging Feature

* Added `AuditLog` model to record user actions and events for security and compliance.
* Implemented API endpoint `/api/export-auditlog/` to export audit logs as CSV or plain text log file (`.log`).
	- Usage: `/api/export-auditlog/?format=csv` or `/api/export-auditlog/?format=log`

---

### November 2025 - Notification Preferences & Email Summaries

* Added `NotificationPreference` model for user notification settings (enable/disable, report frequency).
* Created API endpoint `/api/notification-preferences/` (GET/PUT) for users to manage notification preferences.
* Implemented summary email utility and management command to send daily/weekly/monthly FarmBot activity reports to users.
* Configured SMTP/email settings via `.env` and `settings.py` for secure email delivery.
* Only users with notifications enabled and matching frequency receive summary emails.

---

#### What's new
New tool functionalities:
* Implemented Watering Tool functionality (frontend & backend)
* Implemented Weeder Tool functionality (frontend & backend)
* Added support for the Rotary Tool (backend)
* Added Seed Injector capabilities (backend)
* Added Soil Sensor readings (backend)

Other changes:
* Created a run script to quickly setup everything
* OAuth2 implementation (for logging in with Google or Github)
* Migrated to Daphne as default ASGI server
* Added Docker support with docker-compose
* Implemented WebSocket for live updates
* Added a photo gallery to conveniently view all photos
* Implemented sequence editor API
* Created the web app logo
* Updated the design in figma