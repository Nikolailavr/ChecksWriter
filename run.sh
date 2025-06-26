#!/bin/bash

docker-compose down bot celery-1 flower
docker volume prune -f
docker-compose --env-file ./src/.env up -d --build bot celery-1 flower
docker image prune -f