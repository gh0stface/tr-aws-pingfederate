#!/bin/bash

echo "Starting cluster replication."
curl 'PF_REPLICATE' -X POST \
-H 'x-xsrf-header: PingFederate' \
-H 'authorization: Basic PF_HEADER' \
-H 'accept: application/json';
echo "Replication complete."
