from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt

from rebotics_sdk.hook import views

app_name = 'rebotics_sdk.hook'

urlpatterns = [
    re_path(r'^webhook/(?P<retailer_code>\w+)/$', csrf_exempt(views.WebhookHandlerViewSet.as_view()), name='webhook'),
]
