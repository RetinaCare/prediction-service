#!/bin/bash

uv add -r requirements.txt
cd main && gunicorn app:app --bind 0.0.0.0:8000 --timeout 120
