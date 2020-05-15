#!/bin/bash
gunicorn -w 4 -k gevent main:app --bind 0.0.0.0:80 --daemon