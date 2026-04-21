# Uber Clone Application

A full-stack, responsive Uber alternative built entirely with Django and plain Vanilla JavaScript. This platform replicates core dispatch functionality, driver routing, and interactive GPS mapping utilizing OpenStreetMap Leaflet integration without any frontend frameworks.

## Core Features
*   **Passenger Dashboard:** Seamlessly estimate fares, calculate routes, and book vehicles including Uber Go, Uber Auto, Moto, Rentals, and Packages.
*   **Driver Portal Workflow:** Receive dynamic live pings for incoming ride requests natively categorized by your specific vehicle credentials.
*   **Interactive Cartography:** Fully working `Leaflet.js` mapped integration utilizing OpenStreetMaps and Nominatim Geocoding for live GPS coordinate conversion. 
*   **Live Trip Tracking:** Real-time mock physical vehicle movement animations during active rides with ETA calculations.
*   **Secure Authentication:** End-to-end OTP 2FA authorization logic for rider validation, alongside exclusive login pathways limiting generic users from entering driver portals.
*   **Stripe Integration:** Built-in connection capabilities for processing functional card payments prior to route confirmation. 

## Technology Ecosystem
*   **Backend Framework:** Python / Django 5 
*   **Database:** SQLite3 (Local)
*   **Frontend Interfaces:** Django HTML Templates & Vanilla CSS/JS
*   **Mapping:** Leaflet.js / OpenStreetMaps
*   **Verification:** Twilio Simulation / SMTP Email Auth 

## Setup Instructions

**1. Clone and Activate Environment:**
```bash
git clone https://github.com/Vimuktha-coder/Uber_Application.git
cd Uber_Application
python -m venv venv
venv\Scripts\activate  # Or source venv/bin/activate on Mac/Linux
```

**2. Install Core Dependencies:**
```bash
pip install django stripe requests
```

**3. Database Migrations & Initial Setup:**
```bash
python manage.py makemigrations
python manage.py migrate
python seed.py  # Run this to pre-load the database with test riders and mapped drivers
```

**4. Launch Local Development Server:**
```bash
python manage.py runserver
```
*Navigate to `http://127.0.0.1:8000/` to open the app.*
