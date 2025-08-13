from plugin.registry import plugin_class_registry

from whitebox_plugin_device_manager.whitebox_plugin_device_manager import (
    WhiteboxPluginDeviceManager,
)


map_ = WhiteboxPluginDeviceManager().get_plugin_classes_map()

for key, value in map_.items():
    plugin_class_registry.register(key, value)
