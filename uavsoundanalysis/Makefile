PYTHON := /usr/bin/python3
PIP := /usr/local/bin/pip3

install:
	$(PIP) install -r requirements.txt

lint:
	$(PYTHON) -m black .
	$(PYTHON) -m isort .
	$(PYTHON) -m mypy --config-file mypy.ini .

build:
	powershell docker build -t azrael45/uav .

run:
	powershell docker run -p 8000:8000 azrael45/uav

local:
	$(PYTHON) manage.py runserver