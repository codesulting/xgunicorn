from django.apps import AppConfig

class GunmelConfig(AppConfig):
    name = 'gunmel'
    verbose_name = "Gunmel"

    def ready(self):
        import signals