.PHONY: bootstrap clean server shell test

env = env
project = .
pip = $(env)/bin/pip
python = PYTHONPATH=.:.. $(env)/bin/python

HOST ?= 0.0.0.0
PORT ?= 4354

bootstrap:
	virtualenv --distribute $(env)
	$(pip) install -r requirements.txt

clean:
	find . -name '*.pyc' -delete

server:
	$(python) $(project)/app.py $(HOST):$(PORT)

shell:
	PYTHONPATH=.. $(env)/bin/ipython

test:
	$(python) $(project)/tests.py
