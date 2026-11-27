#!/bin/sh
set -eu

backup_dir=${1:-./backups}
retention_days=${RETENTION_DAYS:-14}
mkdir -p "$backup_dir"
chmod 700 "$backup_dir"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
file="$backup_dir/medflow-$stamp.dump"

docker compose exec -T db pg_dump -U medflow -d medflow -Fc > "$file"
test -s "$file"
find "$backup_dir" -type f -name 'medflow-*.dump' -mtime "+$retention_days" -delete
printf 'Created PostgreSQL backup: %s\n' "$file"
