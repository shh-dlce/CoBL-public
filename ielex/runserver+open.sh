#!/bin/sh
python manage.py runserver &
sleep 5
open http://127.0.0.1:8000/
