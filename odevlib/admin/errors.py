import contextlib

from django.contrib import admin

from odevlib.models.errors import Error

with contextlib.suppress(admin.sites.AlreadyRegistered):
    admin.site.register(Error, admin.ModelAdmin)
