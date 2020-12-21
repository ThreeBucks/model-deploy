#!/bin/bash

set -x
DIR="$(dirname "$(readlink -f "$0")")"
WORKSPACE=$DIR/../

gunicorn server:app -t 60 -b 0.0.0.0:5000 -w 4
