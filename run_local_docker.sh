#!/bin/bash
set -e

# Source .secrets into the host shell first so the ${VAR:-default} fallbacks
# below see its values. -e overrides --env-file in docker run regardless of
# order, so without this, the defaults below would silently clobber whatever
# is in .secrets (e.g. STAGE=prod becoming STAGE=local).
if [ -f .secrets ]; then
    set -a
    # shellcheck disable=SC1091
    source .secrets
    set +a
fi

DATA_DIR="${MAI_DATA_DIR:-$HOME/.local/share/mai-inventory-mgr/data}"
LOG_DIR="${MAI_LOG_DIR:-$HOME/.local/share/mai-inventory-mgr/log}"
mkdir -p "$DATA_DIR" "$LOG_DIR"

docker build -t mai-inventory-mgr -f docker/Dockerfile .

docker rm -f mai-inventory-mgr 2>/dev/null || true

docker run --name="mai-inventory-mgr" \
    --env-file .secrets \
    -e STAGE="${STAGE:-local}" \
    -e LITESTREAM_DISABLE_RESTORE="${LITESTREAM_DISABLE_RESTORE:-1}" \
    -e MAI_DISABLE_LOKI="${MAI_DISABLE_LOKI:-1}" \
    -p 9205:9205 \
    -v "$DATA_DIR":/data \
    -v "$LOG_DIR":/var/log \
    mai-inventory-mgr
