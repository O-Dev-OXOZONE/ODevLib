from django.contrib import admin

from odevlib.models.errors import Error

try:
    admin.site.register(Error, admin.ModelAdmin)
except admin.sites.AlreadyRegistered:
    pass
