from django.db import models
from django.templatetags.static import static


class DeviceType(models.TextChoices):
    CAMERA_360 = "camera_360"
    VIDEO_CAMERA = "video_camera"
    MICROPHONE = "microphone"


device_type_2_icon_url_map = {
    DeviceType.CAMERA_360: static(
        "whitebox_plugin_device_manager/icons/camera_360.svg",
    ),
    DeviceType.VIDEO_CAMERA: static(
        "whitebox_plugin_device_manager/icons/video_camera.svg",
    ),
    DeviceType.MICROPHONE: static(
        "whitebox_plugin_device_manager/icons/microphone.svg",
    ),
}
