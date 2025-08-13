import logging

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
)
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response

from utils.drf.viewsets import SerializersActionMapMixin
from .exceptions import DeviceConnectionException
from .manager import device_manager
from .models import DeviceConnection
from .utils import get_device_instance
from .serializers import (
    DeviceConnectionCreateSerializer,
    DeviceConnectionSerializer,
    SupportedDeviceSerializer,
)


logger = logging.getLogger(__name__)


class DeviceConnectionViewSet(
    SerializersActionMapMixin,
    GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
):
    serializers_action_map = {
        "list": DeviceConnectionSerializer,
        "create": DeviceConnectionCreateSerializer,
    }
    queryset = DeviceConnection.objects.all()

    @action(detail=False, methods=["GET"], url_path="supported-devices")
    def supported_devices(self, request):
        device_classes = device_manager.get_device_classes()

        return Response(
            {
                "supported_devices": [
                    SupportedDeviceSerializer(instance=device_class).data
                    for device_class in device_classes.values()
                ]
            }
        )

    def _verify_connection(self, serializer):
        device = get_device_instance(
            serializer.validated_data["codename"],
            serializer.validated_data["connection_type"],
            serializer.validated_data["connection_settings"],
        )

        error = None

        try:
            device.check_connectivity()
        except DeviceConnectionException as e:
            error = "Could not connect to device: {}".format(str(e))
        except Exception as e:
            logger.exception("Could not connect to device!")
            error = "Could not connect to device: Unknown error"

        if error:
            # Bind error to the top field of the connection type's parameters
            first_field_name = next(
                iter(
                    serializer.validated_data["connection_settings"],
                )
            )

            raise ValidationError(
                {
                    first_field_name: [error],
                }
            )

    def perform_create(self, serializer):
        self._verify_connection(serializer)
        return super().perform_create(serializer)
