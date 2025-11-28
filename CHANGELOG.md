# FarmBot Web App Changelog

## November 2025


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