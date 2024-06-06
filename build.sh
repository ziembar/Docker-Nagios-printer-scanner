#!/bin/bash
set -e

if [ "$(docker ps -q)" ]; then
    docker stop $(docker ps -q)
fi

if [ "$(docker ps -aq)" ]; then
    docker rm -f $(docker ps -aq)
fi

DOCKER_RUN_IMAGE=nagiosprodready

NETWORK=$(ip a | grep -oE 'inet ([0-9]{1,3}\.){3}[0-9]{1,3}/24' | awk '{split($2, ip, "/"); split(ip[1], octets, "."); print octets[1] "." octets[2] "." octets[3] ".0/24"}')

if [ -z "$NETWORK" ]; then
    echo "Nie znaleziono żadnych adresów sieciowych /24."
    exit 1
fi

docker build -t "${DOCKER_RUN_IMAGE}" .
echo "$NETWORK"
docker images
docker run --name "${DOCKER_RUN_IMAGE}" -e "NETWORK=${NETWORK}" -p 8080:80 -t "${DOCKER_RUN_IMAGE}"
