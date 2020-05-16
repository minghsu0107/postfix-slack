#!/bin/bash
# (2*CPU)+1 workers
# log-level: critical, error, info, warning, debug
gunicorn --worker-class=gevent \
         --worker-connections=1000 \
         --workers=9 main:app \
         --bind 0.0.0.0:80 \
         --log-level=warning \
         --log-file ./access.log \
         --daemon