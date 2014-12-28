from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atmospherics.settings')

app = Celery('atmospherics')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object(settings)#'django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

#Copyright 2014 Thorek/Scott and Partners. All Rights Reserved.