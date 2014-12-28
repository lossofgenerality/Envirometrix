#!/bin/bash
cd /var/www/atmospherics/
r=`svn info -r HEAD | grep -i "Last Changed Rev"`
l=`svn info | grep -i "Last Changed Rev"`
if [ "$r" != "$l" ]; then 
	sh deploy.bash > /tmp/auto-deploy.txt
	cat /tmp/auto-deploy.txt | mail -s "Atmospherics auto-deployed" "wayne@devzing.com"
	cat /tmp/auto-deploy.txt | mail -s "Atmospherics auto-deployed" "dara@lossofgenerality.com"
	cat /tmp/auto-deploy.txt | mail -s "Atmospherics auto-deployed" "jacob@lossofgenerality.com"
fi
