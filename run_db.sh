#!/bin/bash

docker volume prune -f
docker-compose -f docker-compose.db.yml --env-file ./src/.env up -d --build
docker image prune -f