from .manager import device_manager


def get_device_instance(codename, connection_type, connection_options):
    device_class = device_manager.get_device_class(codename)
    return device_class(connection_type, connection_options)
