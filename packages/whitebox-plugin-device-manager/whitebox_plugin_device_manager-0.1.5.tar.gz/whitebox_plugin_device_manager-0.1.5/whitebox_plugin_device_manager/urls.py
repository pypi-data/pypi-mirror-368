from rest_framework.routers import SimpleRouter

from .views import (
    DeviceConnectionViewSet,
)


app_name = "whitebox_plugin_device_manager"


router = SimpleRouter()


router.register(
    r"devices",
    DeviceConnectionViewSet,
    basename="device",
)

urlpatterns = router.urls
