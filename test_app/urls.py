from django.conf import settings
from django.urls import path
from rest_framework.routers import BaseRouter, DefaultRouter, SimpleRouter

from test_app.views import (
    ExampleOModelFilteredViewSet,
    ExampleOModelViewSet,
    ExampleRBACChildViewSet,
    ExampleRBACParentViewSet,
    PaginatedExampleOModelViewSet,
)

# Use this file to register DRF views/viewsets for your app.


router: BaseRouter
router = DefaultRouter() if settings.DEBUG else SimpleRouter()


router.register("example_omodel", ExampleOModelViewSet, basename="example_omodel")
router.register("paginated_example_omodel", PaginatedExampleOModelViewSet, basename="paginated_example_omodel")
router.register("example_rbac_parent", ExampleRBACParentViewSet, basename="example_rbac_parent")
router.register("example_rbac_child", ExampleRBACChildViewSet, basename="example_rbac_child")
router.register(
    "paginated_filterset_example_omodel",
    ExampleOModelFilteredViewSet,
    basename="paginated_filterset_example_omodel",
)


app_name = "test_app"
urlpatterns = [
    # path("path/", view=your_view, name="basename"),
] + router.urls
