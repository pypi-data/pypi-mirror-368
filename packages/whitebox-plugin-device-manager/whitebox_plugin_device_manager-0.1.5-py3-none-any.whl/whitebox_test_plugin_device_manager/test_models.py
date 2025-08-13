from django.test import TestCase

from whitebox_plugin_device_manager.base import Device
from whitebox_plugin_device_manager.consts import DeviceType, device_type_2_icon_url_map
from whitebox_plugin_device_manager.manager import device_manager
from whitebox_plugin_device_manager.models import DeviceConnection
from tests.test_utils import DeviceClassResetTestMixin


class TestDevice1(Device):
    codename = "some_camera"
    device_type = DeviceType.CAMERA_360


class TestDevice2(Device):
    codename = "some_drone"


class TestDeviceConnection(DeviceClassResetTestMixin, TestCase):
    def test_get_device_class(self):
        # GIVEN device connection objects that reference registered devices
        device_manager.register_device(TestDevice1.codename, TestDevice1)
        device_manager.register_device(TestDevice2.codename, TestDevice2)

        connection1 = DeviceConnection(codename=TestDevice1.codename)
        connection2 = DeviceConnection(codename=TestDevice2.codename)
        # Test a connection with a device class that is not registered for
        # situations where it might have originated from a plugin that is
        # currently not loaded
        connection3 = DeviceConnection(codename="does_not_exist")

        # WHEN calling the get_device_class method
        device_class1 = connection1.get_device_class()
        device_class2 = connection2.get_device_class()
        device_class3 = connection3.get_device_class()

        # THEN the method should return the correct device class
        self.assertEqual(device_class1, TestDevice1)
        self.assertEqual(device_class2, TestDevice2)
        self.assertIsNone(device_class3)

    def test_get_device_type_icon_url(self):
        # GIVEN device connection objects that reference registered devices,
        #       with and without an icon
        device_manager.register_device(TestDevice1.codename, TestDevice1)
        device_manager.register_device(TestDevice2.codename, TestDevice2)

        connection1 = DeviceConnection(codename=TestDevice1.codename)
        connection2 = DeviceConnection(codename=TestDevice2.codename)
        # Test a connection with a device class that is not registered for
        # situations where it might have originated from a plugin that is
        # currently not loaded
        connection3 = DeviceConnection(codename="does_not_exist")

        # WHEN calling the get_device_class method
        device_icon1 = connection1.get_device_type_icon_url()
        device_icon2 = connection2.get_device_type_icon_url()
        device_icon3 = connection3.get_device_type_icon_url()

        # THEN the method should return the correct device class
        self.assertEqual(
            device_icon1,
            device_type_2_icon_url_map[TestDevice1.device_type],
        )
        self.assertIsNone(device_icon2)
        self.assertIsNone(device_icon3)
