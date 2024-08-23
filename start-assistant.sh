#!/bin/bash

WORKSPACE_BASE=$(pwd)
docker run -it \
    --pull=always \
    -e WORKSPACE_MOUNT_PATH=$WORKSPACE_BASE \
    -e SANDBOX_USER_ID=0 \
    -v $WORKSPACE_BASE:/opt/workspace_base \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -p 3000:3000 \
    --add-host host.docker.internal:host-gateway \
    --name openhands-app-$(date +%Y%m%d%H%M%S) \
    ghcr.io/all-hands-ai/openhands:main

#    -e SANDBOX_USER_ID=$(id -u) \