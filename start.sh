#!/bin/sh
#cd /code/seedcross
python manage.py process_tasks &
python manage.py runserver 0.0.0.0:8019