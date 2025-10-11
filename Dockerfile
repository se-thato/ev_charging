# Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required for building wheels and common libs
# - mysqlclient: default-libmysqlclient-dev (or libmariadb-dev on some distros)
# - psycopg2-binary: libpq-dev (binary usually ok but keep headers handy)
# - cryptography/cffi, lxml, pillow: build-essential, libssl-dev, libffi-dev, libxml2-dev, libxslt1-dev, zlib1g-dev, libjpeg
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       pkg-config \
       libpq-dev \
       libmariadb-dev \
       libmariadb-dev-compat \
       libssl-dev \
       libffi-dev \
       libxml2-dev \
       libxslt1-dev \
       zlib1g-dev \
       libjpeg62-turbo-dev \
    && rm -rf /var/lib/apt/lists/*

# Setting workdir
WORKDIR /app
# Ensure expected runtime directories exist
RUN mkdir -p /app/static /app/media

# Install Python dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copying project files
COPY . .

# Expose application port
EXPOSE 8000

# Default command: run migrations, collect static, then start Gunicorn
# For Channels (ASGI) you may swap gunicorn with daphne:
#   daphne -b 0.0.0.0 -p 8000 ev_charging.asgi:application
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn ev_charging.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-3}"]
