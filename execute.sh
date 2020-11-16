#!/bin/bash
echo "Staring Cluster build..."
yarn install || exit 1
echo "Creating Containers..."
make
sleep 1
echo "Creating Merkle Database..."
cd timber/
yarn install || exit 1
echo "Preparing Contract Deployments and test network..."
docker-compose up -d
sleep 1
echo "==> Loading Clusters, this may take a few minutes"
sleep 5
echo "See Console for more information"
