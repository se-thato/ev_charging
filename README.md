# VoltHub EV Charging Platform

VoltHub is a web-based platform for electric vehicle (EV) charging. It uses Django, Django REST Framework, Channels (ASGI/WebSockets), Celery, and Redis to deliver authentication, charging stations, bookings, e-commerce, real-time updates, and user profiles.

## Features

- User Authentication: registration, login, email activation, and profile management.
- Charging Station Management: add, verify, and manage EV stations and charging points.
- Booking & Sessions: reserve time slots and track charging sessions and costs.
- E-commerce: basic payments and transaction history.
- Real-time Updates: WebSockets for live status, notifications, and messaging.
- Admin Dashboard: manage users, stations, and transactions.
- Media: profile pictures and uploads.
- REST API: browsable API and schema docs (Swagger/Redoc if enabled).

## Project Structure (apps)

- authentication/ — auth flows, tokens, and templates
- charging_station/ — stations, bookings, comments, analytics, consumers (WebSockets)
- ecommerce/ — orders/payments permissions
- VoltHub/ — app configs, models, forms, views, static, templates
- ev_charging/ — project settings, URLs, ASGI/WSGI, Celery config
- media/ and profile_pictures/ — uploaded files
- static/ and staticfiles/ — static assets
- virt/ — local virtual environment (optional)

## Requirements

- Python 3.10+ recommended
- pip
- Redis (for Channels and Celery), optional but recommended
- Node/npm only if you plan to build additional frontend assets

## Local Setup

Commands below assume Windows cmd in the project root.

1) Clone
- git clone https://github.com/se-thato/ev_charging.git
- cd ev_charging

2) Virtual environment
- py -m venv virt
- virt\\Scripts\\activate

3) Install dependencies
- pip install -r requirements.txt

4) Environment variables
Create a .env file in the project root (same directory as manage.py) and set values as needed:
- DEBUG=1
- SECRET_KEY=replace-this-with-a-strong-key
- ALLOWED_HOSTS=127.0.0.1,localhost
- DATABASE_URL=sqlite:///db.sqlite3
- EMAIL_HOST=
- EMAIL_PORT=
- EMAIL_HOST_USER=
- EMAIL_HOST_PASSWORD=
- EMAIL_USE_TLS=1
- REDIS_URL=redis://127.0.0.1:6379/0
- CELERY_BROKER_URL=redis://127.0.0.1:6379/1
- CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/2

Check ev_charging/settings.py for the exact environment variable names if they differ.

5) Database
- python manage.py migrate
- python manage.py createsuperuser

6) Static and media
- python manage.py collectstatic --noinput
Media uploads are saved under media/ and profile_pictures/ during development.

7) Run the app
- python manage.py runserver
Open http://127.0.0.1:8000/

## Real-time and Background Tasks

- Channels (WebSockets): ASGI is configured via ev_charging/asgi.py and app routing under charging_station/routing.py. Ensure Redis is running locally: redis-server.
- Celery: start workers after Redis is running:
  - celery -A ev_charging worker -l info
  - celery -A ev_charging beat -l info

## API and Docs

- Browsable API via DRF at the relevant endpoints.
- Swagger/OpenAPI if configured (commonly at /swagger/ or /api/schema/). Check ev_charging/urls.py and app urls.py for the current routes.

## Running Tests

- python manage.py test

## Docker (optional)

A Dockerfile is included. Example development build/run:
- docker build -t volthub:dev .
- docker run -p 8000:8000 volthub:dev
If using Redis/Celery, run Redis in another container and set env vars accordingly.

## Common Management Commands

- Create migrations: python manage.py makemigrations
- Apply migrations: python manage.py migrate
- Create superuser: python manage.py createsuperuser
- Collect static: python manage.py collectstatic
- Load sample data: python manage.py loaddata <fixture.json>

## Folder Notes

- templates/VoltHub/*: HTML templates including base.html, profile, messaging, submit station
- authentication/templates/*: activation emails and auth pages
- static/: place custom CSS/JS/images during development

## Admin and Access

- Admin: http://127.0.0.1:8000/admin/
- Default login/register paths are under authentication/urls.py as configured in ev_charging/urls.py

## Contributing

- Create a feature branch
- Follow PEP8/Black style where applicable
- Write tests for new behavior
- Open a PR with a clear description

## License

This repository does not specify a license. Add one if you plan to distribute publicly.

## Support

Open an issue in the repository with steps to reproduce problems or feature requests.