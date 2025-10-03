from .celery import app as celery_app

__all__ = ("celery_app",)



# Ensure PyMySQL is used as MySQLdb for Django's MySQL backend.
# This must be imported as early as possible during project startup.
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    # If PyMySQL isn't installed in some environments (e.g., local SQLite dev),
    # silently ignore to avoid breaking non-MySQL configurations.
    pass


