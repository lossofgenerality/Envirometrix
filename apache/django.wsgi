import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'atmospherics.settings'
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

path = BASE_DIR
if path not in sys.path:
    sys.path.append(path)

#Copyright 2014 Thorek/Scott and Partners. All Rights Reserved.

