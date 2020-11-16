#!/usr/bin/env sh

apt-get update

apt-get install -y bash make nmap gcc g++

curl https://deb.nodesource.com/setup_14.x | bash -

apt -y install nodejs

rm -rf /var/lib/apt/lists/*
