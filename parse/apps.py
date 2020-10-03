from django.apps import AppConfig


class ParseConfig(AppConfig):
    name = 'parse'

    def ready(self):
        from add_updater import updater
        updater.start()