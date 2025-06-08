#!/bin/bash

docker volume prune -f
docker compose --env-file ./src/.env up -d --build
docker image prune -f