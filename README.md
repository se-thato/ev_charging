# VoltHub EV Charging Platform

VoltHub is a web-based platform designed to provide efficient and accessible solutions for electric vehicle (EV) charging systems. The project leverages Django and Django REST Framework to offer a robust backend for managing authentication, charging stations, e-commerce features, and user profiles.

## Features

- **User Authentication:** Secure registration, login, and profile management.
- **Charging Station Management:** Add, view, and manage EV charging stations.
- **Booking System:** Users can book charging slots at available stations.
- **E-commerce Integration:** Support for payments and transaction history.
- **Real-time Updates:** WebSocket support for live charging status and notifications.
- **Admin Dashboard:** Manage users, stations, and transactions.
- **Media Support:** Upload and manage profile pictures.
- **REST API:** Well-documented API endpoints for integration and automation.

## Project Structure


- `authentication/` - Handles user authentication and authorization.
- `charging_station/` - Manages charging station data and real-time communication.
- `ecommerce/` - Manages payment and transaction features.
- `VoltHub/` - Main Django project configuration and settings.
- `media/` & `profile_pictures/` - Stores uploaded user files.
- `staticfiles/` - Static assets (CSS, JS, images).
- `virt/` - Python virtual environment.

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- Node.js (for frontend dependencies, if any)

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/se-thato/ev_charging.git
   cd ev_charging

2. **Create and activate a virtual environment:**
- python -m venv virt
- source virt/bin/activate


3. **Install Python dependencies:**
- pip install -r requirements.txt

4. **Apply migrations:**
- python manage.py migrate

5. **Create a superuser (admin):**
- python manage.py migrate

6. **Run the development server:**
- python manage.py runserver

7. **Access the app:**
- Visit http://127.0.0.1:8000/ in your browser.


## API Documentation
- Interactive API documentation is available via Swagger at:
- http://127.0.0.1:8000/swagger/


For more information, see the VoltHub/about_us.html page.