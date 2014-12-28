from __future__ import absolute_import
from django.contrib import admin
import logger.models as models
from django.template.defaultfilters import truncatechars
from filters import StringFilter, DateRangeFilter


# Register your models here.
class LogAdmin(admin.ModelAdmin):
    list_display = (
        'status',
        'subsystem',
        'truncated_message',
        'elapsed_time',
        'time_stamp',
        )
    list_filter = (
        'status',
        'subsystem',
        ('message', StringFilter),
        ('time_stamp', DateRangeFilter),
    )
    readonly_fields=('message','status', 'time_stamp', 'elapsed_time', 'subsystem')

    def truncated_message(self, obj):
        return truncatechars(obj.message, 50)

admin.site.register(models.Log, LogAdmin)
