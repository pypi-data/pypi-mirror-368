from copy import deepcopy

from django.template import loader

from .consts import DeviceType


class DeviceWizard:
    wizard_step_config: list = None
    wizard_step_context: dict = None

    @classmethod
    def get_connection_types(cls) -> dict:
        raise NotImplementedError

    @classmethod
    def get_wizard_step_context(cls) -> dict:
        return cls.wizard_step_context or {}

    @classmethod
    def get_wizard_step_config(cls) -> list:
        if cls.wizard_step_config is None:
            raise ValueError("Wizard step config not set")

        step_config = deepcopy(cls.wizard_step_config)
        step_context = cls.get_wizard_step_context()

        for step in step_config:
            template_name = step["template"]
            renderer = loader.get_template(template_name)
            rendered_template = renderer.render(context=step_context)
            step["template"] = rendered_template

        return step_config


class Device:
    device_type: DeviceType = None
    device_image_url: type(str) = None
    wizard_class: type[DeviceWizard] = None

    @property
    def codename(self):
        raise NotImplementedError

    @property
    def device_name(self):
        raise NotImplementedError

    @classmethod
    def get_wizard_class(cls):
        if getattr(cls, "wizard_class", None):
            return cls.wizard_class

        raise ValueError("Wizard class not set")

    @classmethod
    def get_connection_types(cls) -> dict:
        """
        Get the connection types and their options for the device.

        Returns:
            A mapping containing the connection options.
        """
        return cls.get_wizard_class().get_connection_types()

    def __init__(self, connection_type, connection_options):
        self.connection_type = connection_type
        self.connection_options = connection_options

    def check_connectivity(self) -> bool:
        """
        Check the connection to the device.

        :return: Whether the device was connected
        """
        raise NotImplementedError
