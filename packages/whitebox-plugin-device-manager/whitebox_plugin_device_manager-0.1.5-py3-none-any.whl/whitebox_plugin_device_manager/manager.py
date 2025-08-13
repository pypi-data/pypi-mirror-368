import threading


class DeviceManager:
    """
    Singleton class for managing devices.

    Attributes:
        _devices: A map of loaded device classes.
        _lock: A lock to ensure thread safety.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._lock = threading.Lock()
            cls._instance._devices = {}
        return cls._instance

    def get_device_class(self, codename):
        try:
            return self._devices[codename]
        except KeyError:
            raise ValueError(
                "Device with codename {} not found".format(codename),
            )

    def get_device_classes(self):
        return self._devices

    def register_device(self, codename, device_class):
        with self._lock:
            if codename in self._devices:
                raise ValueError(
                    "Device with codename {} already registered (class: {})".format(
                        codename,
                        self._devices[codename].__name__,
                    ),
                )

            self._devices[codename] = device_class
            # Add the codename to the class, overriding the property
            setattr(device_class, "_codename", codename)

    def unregister_device(self, codename):
        with self._lock:
            if codename not in self._devices:
                raise ValueError(
                    "Device with codename {} not found".format(codename),
                )

            del self._devices[codename]


device_manager = DeviceManager()
