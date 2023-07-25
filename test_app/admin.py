from django.contrib import admin

from test_app.models import ExampleOModel
from odevlib.admin import OModelAdmin


@admin.register(ExampleOModel)
class ExampleOModelAdmin(OModelAdmin):
    pass
