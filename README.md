# Requirements

You'll need to install Python, gunicorn, and the Flask libraries:

```sudo pip install flask flask-socketio flask-mysql gunicorn```

You'll also need to setup MySQL and NGINX/Apache (not expalined here)


# Setup

## Make the MySQL table

Login to your MySQL table. To make a new database with table and permissions you can use the following:

```
create database DB_NAME;
create table text(id MEDIUMINT NOT NULL AUTO_INCREMENT, sitename varchar(200) NOT NULL, document LONGTEXT NOT NULL, version MEDIUMINT UNSIGNED NOT NULL, date_modified DATETIME, date_created DATETIME, PRIMARY KEY(id));
create user 'USER_NAME'@'127.0.0.1' identified by 'PASSWORD';
GRANT ALL PRIVILEGES ON DB_NAME.* to 'USER_NAME'@'127.0.0.1';
```

where you need to change ```DB_NAME, USER_NAME, PASSWORD``` to your choosing.

## Setup ```server.py```

In ```server.py``` modify the MySQL parameters to match the ones that you made for your MySQL database.

That's it!

# Running

To run you'll need to use Gunicorn with a socketio worker class:

```
gunicorn --worker-class socketio.sgunicorn.GeventSocketIOWorker -b 127.0.0.1:5000 server:app
```
