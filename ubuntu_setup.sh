#!/bin/bash

apt -y update
apt -y upgrade
apt -y install git redis-server python3-pip ffmpeg nginx snapd ufw gpg-agent htop nano mailutils

git config --global credential.helper store
cd /rDrama
git config branch.frost.rebase true
cp ./env_template ./.env
. ./.env

mkdir /scripts
cp ./startup.sh /scripts/s
cp ./startup_chat.sh /scripts/s2
chmod +x /scripts/*

sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
apt -y update
apt -y install postgresql-14
rm /etc/postgresql/14/main/pg_hba.conf
cp pg_hba.conf /etc/postgresql/14/main/pg_hba.conf
service postgresql restart
chown postgres:postgres /etc/postgresql/14/main/pg_hba.conf

rm /etc/nginx/sites-available -r
rm /etc/nginx/sites-enabled/default
mkdir /etc/nginx/includes
cp nginx.conf /etc/nginx/sites-enabled/1
cp nginx-serve-static.conf /etc/nginx/includes/serve-static
cp nginx-headers.conf /etc/nginx/includes/headers
/etc/init.d/nginx reload

psql -U postgres -f schema.sql postgres
psql -U postgres -f seed-db.sql postgres
pip3 install -r requirements.txt

mkdir /images
mkdir /chat_images
mkdir /dm_images
mkdir /songs
mkdir /videos
mkdir /audio
mkdir /asset_submissions
mkdir /asset_submissions/marseys
mkdir /asset_submissions/hats
mkdir /asset_submissions/marseys/original
mkdir /asset_submissions/hats/original
mkdir /var/log/rdrama

chown rdrama:rdrama /var/log/rdrama

git config --global --add safe.directory /songs
git config --global --add safe.directory /images
git config --global --add safe.directory /videos
git config --global --add safe.directory /audio

snap install opera-proxy

ufw allow ssh
ufw allow from 173.245.48.0/20
ufw allow from 103.21.244.0/22
ufw allow from 103.22.200.0/22
ufw allow from 103.31.4.0/22
ufw allow from 141.101.64.0/18
ufw allow from 108.162.192.0/18
ufw allow from 190.93.240.0/20
ufw allow from 188.114.96.0/20
ufw allow from 197.234.240.0/22
ufw allow from 198.41.128.0/17
ufw allow from 162.158.0.0/15
ufw allow from 104.16.0.0/13
ufw allow from 104.24.0.0/14
ufw allow from 172.64.0.0/13
ufw allow from 131.0.72.0/22
echo "y" | ufw enable

curl https://rclone.org/install.sh | bash
echo "psql -U postgres" > /p
echo "cd /rDrama && git pull" > /g

. imei.sh
