import unittest

from whitebox_plugin_device_manager.manager import device_manager


global original_device_classes


class TestDeviceManager(unittest.TestCase):
    # Use the setUpClass and tearDownClass methods to save and restore the
    # original device classes before and after the tests
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        global original_device_classes
        original_device_classes = device_manager.get_device_classes()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        device_manager.get_device_classes().clear()
        device_manager.get_device_classes().update(original_device_classes)

    def setUp(self):
        super().setUp()
        device_manager.get_device_classes().clear()

    def tearDown(self):
        super().tearDown()
        device_manager.get_device_classes().clear()

    def test_register_device(self):
        # GIVEN a test device class that will be registered
        device_codename = "test_device"

        class DeviceClass:
            codename = device_codename

        # WHEN the test device class is registered
        device_manager.register_device(device_codename, DeviceClass)
        new_state = device_manager.get_device_classes()

        # THEN the device manager should contain the test device class
        self.assertEqual(
            new_state,
            {device_codename: DeviceClass},
        )

    def test_register_duplicate_device(self):
        # GIVEN a test device class that will be registered
        device_codename = "test_device"

        class DeviceClass:
            pass

        # WHEN the test device class is registered twice
        # THEN a ValueError should be raised
        device_manager.register_device(device_codename, DeviceClass)
        with self.assertRaises(ValueError):
            device_manager.register_device(device_codename, DeviceClass)

    def test_get_device_class(self):
        # GIVEN a test device class that will be registered
        device_codename = "test_device"

        class DeviceClass:
            pass

        # WHEN the test device class is registered
        device_manager.register_device(device_codename, DeviceClass)

        # THEN the device manager should return the test device class when
        #      queried for it by device codename
        self.assertEqual(
            device_manager.get_device_class(device_codename),
            DeviceClass,
        )

    def test_get_device_class_not_found(self):
        # GIVEN a device manager with no devices registered (initial state)
        # WHEN trying to get a device class that is not registered
        # THEN a ValueError should be raised
        with self.assertRaises(ValueError):
            device_manager.get_device_class("test_device")

    def test_unregister_device(self):
        # GIVEN a test device class that will be registered
        device_codename = "test_device"

        class DeviceClass:
            pass

        # WHEN the test device class is registered and then unregistered
        device_manager.register_device(device_codename, DeviceClass)
        device_manager.unregister_device(device_codename)

        # THEN the device manager should not contain the test device class
        self.assertNotIn(
            device_codename,
            device_manager.get_device_classes(),
        )

    def test_unregister_unexisting_device(self):
        # GIVEN a device manager that does not have some device registered
        # WHEN trying to unregister that device
        # THEN a ValueError should be raised
        with self.assertRaises(ValueError):
            device_manager.unregister_device("insta404")
