#!/bin/bash

set -x
DIR="$(dirname "$(readlink -f "$0")")"
WORKSPACE=$DIR/../

gunicorn server:app -b 0.0.0.0:5000 -w 4
