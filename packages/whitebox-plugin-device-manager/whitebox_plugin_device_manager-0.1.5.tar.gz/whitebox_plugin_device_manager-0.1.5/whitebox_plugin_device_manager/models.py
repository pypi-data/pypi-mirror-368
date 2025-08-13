from django.db import models

from utils.models import TimestampedModel
from .manager import device_manager
from .consts import device_type_2_icon_url_map


class DeviceConnection(TimestampedModel):
    name = models.CharField(max_length=128, unique=True)
    codename = models.CharField(max_length=128)

    connection_type = models.CharField(max_length=128)
    connection_settings = models.JSONField()

    def __str__(self):
        return "{} ({})".format(self.name, self.codename)

    def get_device_class(self) -> type["Device"]:
        try:
            return device_manager.get_device_class(self.codename)
        except ValueError:
            return None

    def get_device_type_icon_url(self):
        device_class = self.get_device_class()
        if not device_class:
            return None

        return device_type_2_icon_url_map.get(device_class.device_type)
