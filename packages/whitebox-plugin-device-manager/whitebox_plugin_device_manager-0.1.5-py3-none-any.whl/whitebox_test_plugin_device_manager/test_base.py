from unittest.mock import MagicMock, patch
from django.test import TestCase

from whitebox_plugin_device_manager.base import (
    Device,
    DeviceWizard,
)


class TestDeviceBase(TestCase):
    def test_class_methods_when_valid(self):
        # GIVEN a Device subclass with everything setup
        wizard_class_mock = MagicMock()

        class TestDevice(Device):
            wizard_class = wizard_class_mock

        # WHEN methods are called
        # THEN they should return proper proxied values
        self.assertIs(TestDevice.get_wizard_class(), wizard_class_mock)

        connection_types = TestDevice.get_connection_types()
        wizard_class_mock.get_connection_types.assert_called_once_with()
        self.assertIs(
            connection_types,
            wizard_class_mock.get_connection_types.return_value,
        )

    def test_class_methods_when_not_configured_properly(self):
        # GIVEN a Device class with nothing setup
        class TestDevice(Device):
            pass

        # WHEN methods are called
        # THEN they should raise NotImplementedError
        with self.assertRaises(ValueError):
            TestDevice.get_wizard_class()


class TestDeviceWizardBase(TestCase):
    def test_class_methods_when_valid(self):
        # GIVEN a DeviceWizard subclass with everything setup
        wizard_step_context_mock = MagicMock()

        class TestDeviceWizard(DeviceWizard):
            wizard_step_context = wizard_step_context_mock

        # WHEN methods are called
        # THEN they should return proper proxied values
        self.assertIs(
            TestDeviceWizard.get_wizard_step_context(),
            wizard_step_context_mock,
        )

    def test_class_methods_when_not_configured_properly(self):
        # GIVEN a Device class with nothing setup
        class TestDeviceWizard(DeviceWizard):
            pass

        # WHEN methods are called
        # THEN they should raise NotImplementedError
        with self.assertRaises(ValueError):
            TestDeviceWizard.get_wizard_step_config()

    @patch("django.template.loader.get_template")
    def test_wizard_step_config_formatting(self, mock_get_template):
        # GIVEN a DeviceWizard subclass with a step config and context
        template_name = "ship-of-theseus.html"

        class TestDeviceWizard(DeviceWizard):
            wizard_step_config = [
                {
                    "template": template_name,
                },
            ]
            wizard_step_context = {
                "hello": "qwerty",
                "world": "azerty",
            }

        # WHEN the step config is requested
        rendered = TestDeviceWizard.get_wizard_step_config()

        # THEN it should be formatted properly
        mock_get_template.assert_called_once_with(template_name)
        mock_get_template.return_value.render.assert_called_once_with(
            context=TestDeviceWizard.wizard_step_context,
        )

        self.assertEqual(
            rendered[0]["template"],
            mock_get_template.return_value.render.return_value,
        )
