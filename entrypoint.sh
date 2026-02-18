#!/bin/sh
set -e

PUID=${PUID:-1000}
PGID=${PGID:-1000}
TZ=${TZ:-Europe/Berlin}

if ! grep -q "^[^:]*:[^:]*:${PGID}:" /etc/group; then
  groupadd -g "${PGID}" appgroup
fi

if ! id -u appuser >/dev/null 2>&1; then
  useradd -u "${PUID}" -g "${PGID}" -M -s /usr/sbin/nologin appuser
fi

chown -R "${PUID}:${PGID}" /app/data

export TZ

exec gosu "${PUID}:${PGID}" "$@"
