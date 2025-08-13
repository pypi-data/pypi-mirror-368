import unittest
from unittest.mock import patch, Mock

from whitebox_plugin_device_manager.manager import DeviceManager
from whitebox_plugin_device_manager.utils import get_device_instance


class TestDeviceManager(unittest.TestCase):
    def setUp(self):
        self.device_manager = DeviceManager()

    def test_get_device_instance(self):
        # GIVEN a test device class that will be registered and then invoked
        #       with these parameters
        device_codename = "test_device"
        connection_type = "test_type"
        connection_params = {"test_param": "test_value"}
        expected_instance = object()
        DeviceClass = Mock(return_value=expected_instance)

        with patch(
            "whitebox_plugin_device_manager.utils.device_manager",
            self.device_manager,
        ):
            # WHEN the test device class is registered
            self.device_manager.register_device(device_codename, DeviceClass)

            # THEN the device manager should return an instance of the test
            #      device class with the input parameters
            device_instance = get_device_instance(
                device_codename,
                connection_type,
                connection_params,
            )

        DeviceClass.assert_called_once_with(connection_type, connection_params)
        self.assertEqual(device_instance, expected_instance)
