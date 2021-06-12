#!/bin/bash

#讀取.env
source .env

TOKEN=$INLETS_TOKEN
REMOTE=$INLETS_REMOTE
LOCAL_URL=$INLETS_LOCAL_URL
VERSION=$INLETS_VERSION

if [ ! -f "./inlets" ]; then
    wget "https://github.com/inlets/inlets/releases/download/$VERSION/inlets" -O "./inlets"
fi

chmod u+x ./inlets
./inlets client --url=$REMOTE --upstream=$LOCAL_URL --token $TOKEN