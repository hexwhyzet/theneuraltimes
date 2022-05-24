from django.apps import AppConfig


class TheneuraltimesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'theneuraltimes_app'

    def ready(self):
        import os
        import sys
        from theneuraltimes_app.telegram import first_fake_poll, initialize_admin_state
        from theneuraltimes_app.scheduler import start_scheduler

        if os.environ.get('RUN_MAIN', None) != 'true' and 'runserver' in sys.argv:
            first_fake_poll()
            initialize_admin_state()
            start_scheduler()
            pass
