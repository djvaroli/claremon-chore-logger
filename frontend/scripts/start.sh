#!/bin/bash

[[ -z "$PORT" ]] && export PORT=8080
exec http-server dist -p "$PORT"