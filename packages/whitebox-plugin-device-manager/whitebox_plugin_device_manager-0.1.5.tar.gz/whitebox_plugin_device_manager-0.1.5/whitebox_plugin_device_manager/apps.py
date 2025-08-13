from django.apps import AppConfig

from plugin.registry import model_registry


class WhiteboxPluginDeviceManagerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "whitebox_plugin_device_manager"
    verbose_name = "Device Manager"

    def ready(self):
        # TODO: Move this to `Plugin.plugin_model_classes_map` when hybrid
        #       plugin concept is finalized
        from .models import DeviceConnection

        model_registry.register("device.DeviceConnection", DeviceConnection)
