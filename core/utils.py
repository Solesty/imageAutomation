from .models import Settings


def getOrCreateSettingsObject():
    """ Creates a new settings instance with the default values 
        or gets the old settings instance.
        Always call this rather than creating a new settings object
        for the application.
    """

    if Settings.objects.all().count() == 0:
        return Settings.objects.create()
    else:
        return Settings.objects.all().first()
