#!/bin/bash
# install docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo service docker start
# start mysql daemon
sudo docker compose up -d
# initialize database
sudo docker exec flask-mysql /bin/sh -c "mysql -uroot -pexample < /db/setup.sql"
# create virtualenv
python -m venv env
source ./env/bin/activate
pip install -r requirements.txt