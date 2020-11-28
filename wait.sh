#!/bin/sh

set -e
  
cmd="$@"

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 2
done

# sleep 10

>&2 echo "Postgres is up - executing command"
exec $cmd