from django.apps import AppConfig


# https://stackoverflow.com/questions/2781383/where-to-put-django-startup-code
def startup():
    from crseed.views import startCrossSeedRoutine
    print('(crseed.tasks) Start a routine to cross seed.')
    startCrossSeedRoutine()


class CrseedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crseed'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN'):
            startup()


