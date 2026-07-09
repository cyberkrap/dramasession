#!/bin/bash

cd /rDrama
. ./.env
gunicorn files.__main__:app -w 3
