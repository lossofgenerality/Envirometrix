from django.db import models
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

class Log(models.Model):

    status_options = (
                    ('info', 'Information'),
                    ('debug', 'Debug'),
                    ('error', 'Error'),
                    ('warning', 'Warning'),
                    )

    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=status_options, default='info')
    subsystem = models.CharField(max_length=100, default='', blank=True)
    time_stamp = models.DateTimeField(default=timezone.now, blank=True)
    elapsed_time = models.DecimalField(decimal_places=10, max_digits=30, blank=True, null=True)

    time_stamp.date_range_filter = True
    time_stamp.show_media = True

    def __unicode__(self):
        return "[{}: {}/{}] {}".format(self.time_stamp, self.status, self.subsystem, self.message)

    @staticmethod
    @transaction.atomic
    def log(status, subsystem, message, time_stamp=None, elapsed_time=None):
        dic = {'status':status, 'subsystem':subsystem, 'message':message}
        if time_stamp is not None:
            dic['time_stamp'] = time_stamp
        if elapsed_time is not None:
            dic['elapsed_time'] = Decimal(str(elapsed_time))

        return Log.objects.create(**dic)

    @staticmethod
    def info(subsystem, message, time_stamp=None, elapsed_time=None):
        return Log.log('info', subsystem, message, time_stamp, elapsed_time)

    @staticmethod
    def debug(subsystem, message, time_stamp=None, elapsed_time=None):
        return Log.log('debug', subsystem, message, time_stamp, elapsed_time)

    @staticmethod
    def warning(subsystem, message, time_stamp=None, elapsed_time=None):
        return Log.log('warning', subsystem, message, time_stamp, elapsed_time)

    @staticmethod
    def error(subsystem, message, time_stamp=None, elapsed_time=None):
        return Log.log('error', subsystem, message, time_stamp, elapsed_time)
