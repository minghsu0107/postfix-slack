#!/bin/bash
# (2*CPU)+1 workers
gunicorn --worker-class=gevent \
         --worker-connections=1000 \
         --workers=9 main:app \
         --bind 0.0.0.0:80 \
         --daemon