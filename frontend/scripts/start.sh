#!/bin/bash

[[ -z "$PORT" ]] && export PORT=8080
envsubst "$PORT" < /.ngnix/nginx.conf.in > /.nginx/nginx.conf

exec nginx -c /.ngnix/nginx.conf