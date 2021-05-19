#!/bin/bash

# check that the port env variable is set, otherwise set it to 8080 which should be default
[[ -z "$PORT" ]] && export PORT=8080

# run the app
uvicorn main:app --host 0.0.0.0 --port $PORT