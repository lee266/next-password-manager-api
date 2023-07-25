# Backend of Password manager

## How to start

- Please copy dockercompose_copy and dockercompose_env and ER-dialogram-copy at root dir
- Do docker compose up -d --build
- Do python3 manage.py makemigrations
- Do python3 manage.py migrate

## Database

If you want to see a ER of database

- move to /ER-diagram/mysql.pu
- Do Alt + D
- OR please check /api/ER-diagram-copy/mysql.png

## Commands

if you want join django

- docker exec -it  password_django sh

python update

- python3 manage.py makemigrations
- python3 manage.py migrate

seeder

- python3 manage.py post_initial.json

your first time please do under code

- python3 manage.py createsuperuser

How to see ER diagram

- move to ER-diagram/mysql.pu
- Alt + D
