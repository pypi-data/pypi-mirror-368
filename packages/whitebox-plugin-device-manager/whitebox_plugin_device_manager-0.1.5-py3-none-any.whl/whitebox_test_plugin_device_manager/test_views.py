from unittest.mock import patch

from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient

from whitebox_plugin_device_manager.base import (
    Device,
    DeviceWizard,
)
from whitebox_plugin_device_manager.exceptions import DeviceConnectionException
from whitebox_plugin_device_manager.manager import device_manager
from whitebox_plugin_device_manager.models import DeviceConnection
from tests.test_utils import DeviceClassResetTestMixin, SupressHTTPErrorLoggingMixin


class TestDeviceWizard(DeviceWizard):
    wizard_step_config = []

    @classmethod
    def get_connection_types(cls) -> dict:
        return {
            "wifi": {
                "name": "Wi-Fi",
                "fields": {
                    "ssid": {
                        "name": "Network Name",
                        "type": "text",
                        "required": True,
                    },
                    "password": {
                        "name": "Network Password",
                        "type": "password",
                        "required": True,
                    },
                },
            },
        }


class TestDevice(Device):
    codename = "device_impersonat0r_9000"
    device_name = "Device Impersonat0r 9000"
    wizard_class = TestDeviceWizard

    @classmethod
    def get_connection_types(cls) -> dict:
        return {
            "wifi": {
                "name": "Wi-Fi",
                "fields": {
                    "ssid": {
                        "name": "Network Name",
                        "type": "text",
                        "required": True,
                    },
                    "password": {
                        "name": "Network Password",
                        "type": "password",
                        "required": True,
                    },
                },
            },
        }

    def check_connectivity(self) -> bool:
        return True


global original_device_classes


class TestDeviceViewSet(
    SupressHTTPErrorLoggingMixin,
    DeviceClassResetTestMixin,
    TestCase,
):
    def setUp(self):
        super().setUp()
        device_manager.register_device(TestDevice.codename, TestDevice)
        self.client = APIClient()

    def test_list_supported_devices(self):
        # GIVEN a user is listing all supported devices
        url = reverse("whitebox_plugin_device_manager:device-supported-devices")
        all_device_classes = device_manager.get_device_classes()

        # WHEN the user sends a GET request to the supported devices endpoint
        response = self.client.get(url)

        # THEN the response should be successful and return a list of supported devices
        self.assertEqual(response.status_code, 200)

        device_list = response.json()["supported_devices"]
        for device in device_list:
            codename = device["codename"]
            self.assertIn(codename, all_device_classes)

            device_class = all_device_classes[codename]
            self.assertEqual(device["device_name"], device_class.device_name)
            self.assertEqual(
                device["connection_types"],
                device_class.get_connection_types(),
            )

    def test_list_devices_no_devices(self):
        # GIVEN a user is listing all devices and there are no devices
        url = reverse("whitebox_plugin_device_manager:device-list")

        # WHEN the user sends a GET request to the device list endpoint
        response = self.client.get(url)

        # THEN the response should be successful and return an empty list
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_list_devices_with_devices(self):
        # GIVEN a user is listing all devices and there are devices
        url = reverse("whitebox_plugin_device_manager:device-list")

        device = DeviceConnection.objects.create(
            name="Hubble",
            codename="telescope_interface_wrapper",
            connection_type="antenna",
            connection_settings={
                "test_param": "test_value",
            },
        )

        # WHEN the user sends a GET request to the device list endpoint
        response = self.client.get(url)

        # THEN the response should be successful and return a list of devices
        self.assertEqual(response.status_code, 200)

        expected_response = [
            {
                "id": device.id,
                "name": device.name,
                "codename": device.codename,
                "device_type_icon_url": None,
            }
        ]
        self.assertEqual(response.json(), expected_response)

    @patch.object(TestDevice, "check_connectivity")
    def test_create_device(self, mock_check_connectivity):
        # GIVEN a user is creating a device that is supported, e.g. Insta360X4
        url = reverse("whitebox_plugin_device_manager:device-list")
        data = {
            "name": "My new camera",
            "codename": "device_impersonat0r_9000",
            "connection_type": "wifi",
            "connection_settings": {
                "ssid": "my_ssid",
                "password": "my_password",
            },
        }

        # WHEN the user sends a POST request to the device list endpoint
        response = self.client.post(url, data=data, format="json")

        # THEN the response should be successful, device connectivity has been
        #      verified, and the created device was returned
        self.assertEqual(response.status_code, 201)
        mock_check_connectivity.assert_called_once()

        device = DeviceConnection.objects.get(id=response.json()["id"])
        expected = {
            "id": device.id,
            "name": device.name,
            "codename": device.codename,
        }
        for key, value in expected.items():
            self.assertEqual(response.json()[key], value)

    def test_create_device_with_unsupported_codename(self):
        # GIVEN a user is creating a device
        url = reverse("whitebox_plugin_device_manager:device-list")
        data = {
            "name": "James Webb",
            "codename": "telescope_interface_wrapper",
            "connection_type": "antenna",
            "connection_settings": {},
        }

        # WHEN the user sends a POST request to the device list endpoint
        response = self.client.post(url, data=data, format="json")

        # THEN the response should be a 400 Bad Request, indicating that the
        #      device codename is invalid
        self.assertEqual(response.status_code, 400)

        self.assertIn("codename", response.json())
        self.assertEqual(
            response.json()["codename"][0],
            "Invalid device codename.",
        )

    def test_create_device_with_unsupported_connection_type(self):
        # GIVEN a user is creating a device
        url = reverse("whitebox_plugin_device_manager:device-list")
        data = {
            "codename": "device_impersonat0r_9000",
            "connection_type": "flux_capacitor",
            "connection_settings": {},
        }

        # WHEN the user sends a POST request to the device list endpoint
        response = self.client.post(url, data=data, format="json")

        # THEN the response should be a 400 Bad Request, indicating that the
        #      connection type is invalid
        self.assertEqual(response.status_code, 400)

        self.assertIn("connection_type", response.json())
        self.assertEqual(
            response.json()["connection_type"][0],
            "Invalid connection type for the device.",
        )

    def test_create_device_with_known_error(self):
        # GIVEN a user is creating a device
        codename = "device_impersonat0r_9000"
        connection_type = "wifi"
        device_class = device_manager.get_device_class(codename)

        connection_types = device_class.get_connection_types()
        connection_fields = connection_types[connection_type]["fields"]
        first_connection_field = next(iter(connection_fields))

        expected_error_message = "helloworld.exe"

        url = reverse("whitebox_plugin_device_manager:device-list")
        data = {
            "codename": codename,
            "connection_type": connection_type,
            "connection_settings": {
                "ssid": "my_ssid",
                "password": "my_password",
            },
        }

        # WHEN the user sends a POST request to the device list endpoint, and a
        #      known exception occurs
        with patch.object(
            device_class,
            "check_connectivity",
            side_effect=DeviceConnectionException(expected_error_message),
        ):
            response = self.client.post(url, data=data, format="json")

        # THEN the response should be a 400 Bad Request, indicating that the
        #      device could not be connected to, with a generic error message
        self.assertEqual(response.status_code, 400)
        self.assertIn(first_connection_field, response.json())
        self.assertEqual(
            response.json()[first_connection_field][0],
            "Could not connect to device: {}".format(expected_error_message),
        )

    def test_create_device_with_unknown_error(self):
        # GIVEN a user is creating a device
        codename = "device_impersonat0r_9000"
        connection_type = "wifi"
        device_class = device_manager.get_device_class(codename)

        connection_types = device_class.get_connection_types()
        connection_fields = connection_types[connection_type]["fields"]
        first_connection_field = next(iter(connection_fields))

        url = reverse("whitebox_plugin_device_manager:device-list")
        data = {
            "codename": codename,
            "connection_type": connection_type,
            "connection_settings": {
                "ssid": "my_ssid",
                "password": "my_password",
            },
        }

        # WHEN the user sends a POST request to the device list endpoint, and an
        #      unknown exception occurs
        with (
            patch.object(
                device_class,
                "check_connectivity",
                side_effect=Exception("Random Exception"),
            ),
            # Avoid spam in test output
            patch("logging.Logger.exception"),
        ):
            response = self.client.post(url, data=data, format="json")

        # THEN the response should be a 400 Bad Request, indicating that the
        #      device could not be connected to, with a generic error message
        self.assertEqual(response.status_code, 400)
        self.assertIn(first_connection_field, response.json())
        self.assertEqual(
            response.json()[first_connection_field][0],
            "Could not connect to device: Unknown error",
        )
