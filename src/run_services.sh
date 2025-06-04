#!/bin/bash

# Запуск worker в фоновом режиме
poetry run celery -A app.celery.celery_app worker --pool threads --loglevel=info &

# Запуск flower
poetry run celery -A app.celery.celery_app flower --port=5555
