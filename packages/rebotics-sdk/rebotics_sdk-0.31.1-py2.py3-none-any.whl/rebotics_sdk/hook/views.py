from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rebotics_sdk.hook import signals
from rebotics_sdk.hook.serializers import WebhookDataSerializer


class WebhookHandlerViewSet(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        retailer_code = kwargs['retailer_code']
        serializer = WebhookDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        emitter = signals.SignalEmitter(
            retailer=retailer_code,
            event=serializer.validated_data['event'],
            # do not parse payload, send it as is
            payload=request.data['payload'],
        )
        emitter.emit()

        return Response(status=status.HTTP_202_ACCEPTED)
