from django.conf import settings
from django.urls import path
from rest_framework.routers import BaseRouter, DefaultRouter, SimpleRouter

from test_app.views import ExampleOModelViewSet


# Use this file to register DRF views/viewsets for your app.


router: BaseRouter
if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


router.register("example_omodel", ExampleOModelViewSet, basename="example_omodel")


app_name = "test_app"
urlpatterns = [
    # path("path/", view=your_view, name="basename"),
] + router.urls
