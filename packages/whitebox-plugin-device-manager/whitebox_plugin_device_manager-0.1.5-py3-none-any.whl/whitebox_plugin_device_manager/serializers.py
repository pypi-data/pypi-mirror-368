from rest_framework import serializers

from plugin.registry import import_whitebox_model
from utils.dynamic_fields import generate_dynamic_fields

from .base import Device
from .manager import device_manager
from .models import DeviceConnection


class DeviceConnectionSerializer(serializers.ModelSerializer):
    device_type_icon_url = serializers.CharField(
        source="get_device_type_icon_url",
    )

    class Meta:
        model = DeviceConnection
        fields = ["id", "name", "codename", "device_type_icon_url"]
        extra_kwargs = {
            "codename": {
                "read_only": True,
            },
        }


# region create device connection


class DeviceConnectionSettingsSerializer(serializers.Serializer):
    def __init__(self, *args, device_class, connection_type, **kwargs):
        super().__init__(*args, **kwargs)

        device_fields = self._generate_fields_for_device(
            device_class,
            connection_type,
        )

        self.fields.update(device_fields)

    def _generate_fields_for_device(self, device_class, connection_type):
        connection_types = device_class.get_connection_types()

        if connection_type not in connection_types:
            raise ValueError

        connection_type_options = connection_types.get(connection_type)
        field_config = connection_type_options["fields"]

        device_fields = generate_dynamic_fields(field_config)
        return device_fields


class DeviceConnectionCreateSerializer(serializers.ModelSerializer):
    # Placeholder, will be overwritten by DeviceConnectionSettingsSerializer
    # during validation. This serves to provide a default value for the
    # OPTIONS response.
    connection_settings = serializers.JSONField(default=dict)

    class Meta:
        model = DeviceConnection
        fields = [
            "id",
            "name",
            "codename",
            "connection_type",
            "connection_settings",
        ]
        extra_kwargs = {
            "name": {
                "required": False,
            },
        }

    def validate_codename(self, codename):
        try:
            device_manager.get_device_class(codename)
        except ValueError:
            raise serializers.ValidationError("Invalid device codename.")

        return codename

    def _validate_connection_type(self, device_class, connection_type):
        connection_types = device_class.get_connection_types()

        if connection_type not in connection_types:
            raise serializers.ValidationError(
                {
                    "connection_type": "Invalid connection type for the device.",
                }
            )

    def _validate_connection_settings(
        self,
        device_class,
        connection_type,
        raw_connection_settings,
    ):
        device_fields = DeviceConnectionSettingsSerializer(
            device_class=device_class,
            connection_type=connection_type,
            data=raw_connection_settings,
        )
        if not device_fields.is_valid():
            raise serializers.ValidationError(
                {
                    "connection_settings": device_fields.errors,
                }
            )

        return device_fields.validated_data

    def _ensure_name(self, data, device_class):
        if "name" not in data:
            data["name"] = "{} #{}".format(
                device_class.device_name,
                DeviceConnection.objects.count() + 1,
            )

        return data

    def validate(self, data):
        codename = data["codename"]
        connection_type = data["connection_type"]
        raw_connection_settings = data["connection_settings"]

        device_class = device_manager.get_device_class(codename)

        self._validate_connection_type(device_class, connection_type)

        connection_settings = self._validate_connection_settings(
            device_class,
            connection_type,
            raw_connection_settings,
        )
        data["connection_settings"] = connection_settings

        self._ensure_name(data, device_class)

        return data


# endregion create device connection


# region supported devices


class SupportedDeviceSerializer(serializers.Serializer):
    instance: Device

    codename = serializers.CharField()
    device_name = serializers.CharField()
    device_image_url = serializers.CharField(default=None)
    connection_types = serializers.DictField(source="get_connection_types")
    wizard_steps = serializers.JSONField(
        source="get_wizard_class.get_wizard_step_config",
    )


# endregion supported devices
