#!/bin/bash

# Start the Flask DDNS web application via Gunicorn
tail -f /var/log/ddns.log & \
cd /var/www/html && gunicorn -w 4 -b 0.0.0.0:80 remoteddns:app
