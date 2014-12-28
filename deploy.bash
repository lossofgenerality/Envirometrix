#!/bin/bash
svn update
python manage.py migrate
python manage.py collectstatic --noinput
service celeryd-atmospherics restart
service celerybeat-atmospherics restart
service apache2 restart
echo "Done"