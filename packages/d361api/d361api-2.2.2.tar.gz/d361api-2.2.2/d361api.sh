#!/usr/bin/env bash
PKG=d361api
URL=https://apihub.document360.io/swagger/v2/swagger.json
VER="1.0.0"

openapi-generator-cli generate \
    --api-package $PKG \
    --config $PKG.yaml \
    -g python \
    --git-host github.com \
    --git-repo-id $PKG \
    --git-user-id twardoch \
    -i $URL \
    --minimal-update \
    --model-package $PKG \
    --output . \
    --package-name $PKG \
    --release-note "v$VER" \
    --strict-spec false \
    --verbose

# --remove-operation-id-prefix \
# --skip-overwrite \
