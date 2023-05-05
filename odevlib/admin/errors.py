from django.contrib import admin

from odevlib.admin.omodel import OModelAdmin
from odevlib.models.errors import Error

try:
    admin.site.register(Error, OModelAdmin)
except admin.sites.AlreadyRegistered:
    pass
