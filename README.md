# RedTigers
## Term project for WVU's CS-440 Spring 2025
### Joe Hauser, Tiago Breunig, Ali Sajawal

## Description:
This is a website that allows users to buy and sell PC parts. It maintains a database of devices, that users can add to. Any listing for a specific device selects a device from that database. The website has lots of nice features, including checking CPU and Motherboard compatability and a way to filter listings.
## Tech Stack:
The website is based on [Django](https://www.djangoproject.com/) and uses [MySQL](https://www.mysql.com/) as the database. We also use [Bootstrap](https://getbootstrap.com/) for CSS. We also use [django-bootstrap5](https://github.com/zostera/django-bootstrap5) and the python [mysql connector](https://pypi.org/project/mysql-connector-python/). We also use some of bootstrap's [javascript package](https://www.npmjs.com/package/bootstrap) so that is included as well.
## Prerequisites:
* [python3](https://www.python.org/downloads/)
* [nodejs](https://nodejs.org/en)
* [MySQL Server](https://www.mysql.com/)
## To run:
* clone this repo ```git@github.com:jrhauser/CS440-Red-Tigers.git``` is the ssh string
* create a python [virtual enviornment](https://docs.python.org/3/library/venv.html)
* [activate](https://docs.python.org/3/tutorial/venv.html) the python virtual enviornment
* install the python dependencies ```pip install -r requirements.txt```
* install the javascript dependencies ```npm i```
* [create a database](https://dev.mysql.com/doc/refman/8.4/en/create-database.html) named 'redtiger' on your MySQL server
* Change the settings.py line 83 to be the password for your MySQL server (default is 'root')
* Run the command ```python3 manage.py migrate``` to create the neccesary tables
* Execute both the 'trigger.sql' and 'timezone_fix.sql' scripts in your database
* Run the command ```python3 manage.py import_data``` to add some test data and users
* Run the command ```python3 manage.py runserver```
The website is now running on http://127.0.0.1:8000.
### Default users:
| username | password |
|------- | ------- |
| alexjone1 | apple |
| johnmayors8 | orange |
| greeen_23 | pear |
| woods-tyler9 | mango |
| franklin_gta3 | berry |
| tripper8745 | melon |

