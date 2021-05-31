#!/bin/bash

[[ -z "$PORT" ]] && export PORT=8080
envsubst '$PORT' < .nginx/nginx.conf.in > etc/nginx/nginx.conf

exec nginx -c nginx.conf