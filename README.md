# WMS LOCAL

Dịch vụ cung cấp Web Service, RESTFul API, Schedule Job cho các thiết bị chia chọn tại kho

## Tech Stack

* Python 3.7.x (Framework Django 2.2)
* MySQL
* Redis
* Celery


## Project Layout

```bash
wms_local
├── src
│   └── wms_local
│   │   ├── module1
│   │   ├── module2
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── celeryconf.py
│   │   ├── settings.py
│   │   └── urls.py
│   └── templates
│   └── manage.py
├── .pylintrc
├── requirements.txt
└── README.md
```

## Build and Run 

Create a virtualenv with python3 and install requirement

```bash
cd wms_local
virtualenv env
source env/bin/active
pip3 install -r requirements.txt
```


For dev machine, follow the commands

```bash
cd src
python manage.py runserver
```

