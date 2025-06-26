#!/bin/bash

docker volume prune -f
docker-compose --env-file ./src/.env up -d --build pg redis
docker image prune -f