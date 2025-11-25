#!/bin/bash

uv add -r requirements.txt
cd main && gunicorn app:app --bind 0.0.0.0:3000 --timeout 120
