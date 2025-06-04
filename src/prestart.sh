#!/usr/bin/env bash

set -e

echo "Run apply migrations.."
alembic upgrade heads
echo "Migrations applied!"

exec "$@"