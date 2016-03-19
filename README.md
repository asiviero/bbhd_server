# BBHD Server

Micro app destined to act as a server to https://github.com/machiave/baseballhack

## Setup

Just run `setup.sh`, it will load a virtualenv and install dependencies

## Running the server

```
  $ python flaskr/application.py
```

## Reloading the databse

Remove the sqlite db file, then run `sqlite3 flaskr.db < schema.sql` inside `flaskr` directory.

It should be running on `http://localhost:5000`
