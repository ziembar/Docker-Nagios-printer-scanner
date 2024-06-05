#!/bin/bash
set -e

docker stop $(docker ps -q)
docker rm $(docker ps -aq)

DOCKER_RUN_IMAGE=nagios

NETWORK=$(ip a | grep -oE 'inet ([0-9]{1,3}\.){3}[0-9]{1,3}/24' | awk '{split($2, ip, "/"); split(ip[1], octets, "."); print octets[1] "." octets[2] "." octets[3] ".0/24"}')

if [ -z "$NETWORK" ]; then
    echo "Nie znaleziono żadnych adresów sieciowych /24."
    exit 1
fi

docker build -t "${DOCKER_RUN_IMAGE}" .

docker images
docker run -d --rm --name "${DOCKER_RUN_IMAGE}" -e "${NETWORK}" -p 8080:80 -t "${DOCKER_RUN_IMAGE}"

