# Mission Planning Web Platform

An automated, scalable, and user‑friendly Django-based web application for satellite mission planning and tracking, designed to support resource‑constrained settings.

## Abstract

This research presents an innovative mission planning software suite with a mobile application, designed to assist less developed countries in satellite tracking and operations. It overcomes limitations of traditional tools like Orbitron and GPredict by automating Two‑Line Element (TLE) retrieval (e.g., from CelesTrak) and using the Skyfield library for precise satellite position calculations and pass predictions. Ground station operators can configure imaging parameters, predict optimal pass times, visualize trajectories on interactive maps, save mission plans, and receive automated notifications. All passes and telemetry data are logged in a PostGIS database, and real‑time updates are shared via Telegram integration.

## Features

* **TLE Management**: Automated fetch and persistence of TLE data with database fallback
* **Pass Prediction**: Accurate two‑day horizon pass calculations using Skyfield
* **Mission Planning**: Select satellites, configure imaging parameters, save and retrieve mission plans
* **Interactive Visualization**: Trajectories and ground tracks rendered on a web map (Leaflet)
* **Notifications**: In‑browser push and Telegram alerts for upcoming passes and telemetry updates
* **Telemetry Logging**: Digital storage of pass events and telemetry in PostGIS
* **API Endpoints**: RESTful interfaces for mobile app and Flutter integration

## Prerequisites

* Python 3.8 or newer
* Django 5.x or newer
* Django Channels and Redis
* PostgreSQL with PostGIS extension
* Node.js and npm (for building Tailwind CSS assets)
* Git CLI

## Installation

1. **Clone the repository**

   ```bash
   git clone git@github.com:blezzed/Web_Satellite_Tracking.git
   cd Web_Satellite_Tracking
   ```
2. **Python environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Database setup**

   * Create a PostgreSQL database and enable the PostGIS extension
   * Update `DATABASES` in `settings.py` or via environment variables
4. **Redis (Channels layer)**

   ```bash
   redis-server --daemonize yes
   ```
5. **Environment variables**

   ```bash
   export DJANGO_SECRET_KEY="<your-secret-key>"
   export TELEGRAM_BOT_TOKEN="<your-bot-token>"
   ```
6. **Migrations & Static Assets**

   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
7. **Run the server**

   ```bash
   daphne -b 0.0.0.0 -p 8000 Web_Satellite_Tracking.asgi:application
   ```

## Configuration & Settings

Most application behavior is configured via **`settings.py`** and **`values.py`**:

* **`SECRET_KEY`** and **`DEBUG`**: Controlled via environment or directly in `settings.py` (set `DEBUG=False` in production).
* **`ALLOWED_HOSTS`**: Define hostnames/IPs (e.g., `localhost`, your LAN IPs).
* **`INSTALLED_APPS`** includes:

  * `main` (core app), `satellite_tracker` (tracking logic)
  * REST: `rest_framework`, `rest_framework_simplejwt`, `djoser`
  * Real‑time: `channels`, `webpush`
  * UI: `tailwind`, `theme`, `django_browser_reload`
* **`ASGI_APPLICATION`**: Entry point for WebSockets via Daphne.
* **`CHANNEL_LAYERS`**: Redis at `localhost:6379` for channel communication.
* **`WEBPUSH_SETTINGS`**: VAPID keys and admin email for browser push.
* **Database (`DATABASES`)**: Uses PostGIS engine; schema search path set to `satellite_tracking`.
* **Static & Media**:

  * `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT`
  * `MEDIA_URL`, `MEDIA_ROOT`
* **Tailwind CSS**: Configured via `TAILWIND_APP_NAME = 'theme'` and `NPM_BIN_PATH`.
* **Geo libs** (Windows): `GDAL_LIBRARY_PATH`, `GEOS_LIBRARY_PATH` environment settings.
* **REST & Auth**:

  * JWT auth (`SIMPLE_JWT` with `Bearer` tokens)
  * Djoser serializers for user management
* **Localization**:

  * `LANGUAGE_CODE='en-us'`, `TIME_ZONE='UTC'`, `USE_I18N=True`, `USE_TZ=True`

Adjust these as needed for your environment.

## Usage

* Access **`/mission-plans/`** in the web UI to manage mission configurations
* Connect to **`/ws/passes/`** WebSocket for real-time pass streams
* Use **`/api/`** REST endpoints for mission plans, TLE data, and telemetry logs
* Mobile app integrates via the same API and receives Telegram notifications


## Contributing

1. Fork and create a feature branch
2. Follow PEP8 and include tests
3. Submit a pull request against `main` or `develop`


