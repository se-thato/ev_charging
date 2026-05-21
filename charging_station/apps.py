from django.apps import AppConfig



class ChargingStationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'charging_station'
    
    def ready(self):
        """
        ready() runs once when Django starts up.
        Importing signals here registers all the receivers
        so Django knows to listen for them.
        Without this import, signals.py exists but
        Django never loads it and signals never fire.
        """
        import charging_station.signals