# Backend of Password manager

## Overview

This is api server

## Getting Started

Please copy env

```sh
cp .env.example .env
```

### Git clone

if you want to use monorepo repository, first Please clone it and Check README.md (recommend)
[next-password-manager-monorepo](https://github.com/Lee266/next-password-manager-monorepo)

### Initialize Project

Move to your parent directory.

```sh
docker exec -it password_django sh
python3 manage.py makemigrations
python3 manage.py migrate
```

## Database

If you want to see a ER of database

- move to /ER-diagram/mysql.pu
- Do Alt + D
- Alternatively, check /api/ER-diagram-copy/mysql.png

## Commands

### Join Django Container

- docker exec -it  password_django sh

### Database Migrations

- python3 manage.py makemigrations
- python3 manage.py migrate

### Seeder

- python3 manage.py post_initial.json

For the first time, execute:

- python3 manage.py createsuperuser

## Environments

- Django v4.2.3
- Python v3.10
- Django RestFramework v3.14.0
