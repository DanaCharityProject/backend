#!/bin/sh

docker-compose down
docker-compose build
docker-compose up -d db
docker-compose up -d app
docker-compose exec app flask create_db
docker-compose exec app flask populate_db
