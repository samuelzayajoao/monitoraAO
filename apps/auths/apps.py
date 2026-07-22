from django.apps import AppConfig


class AuthsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auths"  # Must match the full path in INSTALLED_APPS
    label = "auths"  # This forces the app label to be 'auths'
