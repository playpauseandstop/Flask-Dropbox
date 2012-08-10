.PHONY: bootstrap clean server shell test

env = env
env14 = $(env)-1.4
project = .
python = PYTHONPATH=.:.. $(env)/bin/python
python14 = PYTHONPATH=.:.. $(env14)/bin/python

HOST ?= 0.0.0.0
PORT ?= 4354

bootstrap:
	bootstrap.py --copy-virtualenv

clean:
	find . -name '*.pyc' -delete

distclean: clean
	rm -rf build dist $(env) $(env14)

server:
	$(python) $(project)/app.py $(HOST):$(PORT)

shell:
	PYTHONPATH=.:.. $(env)/bin/ipython --color-info --no-banner --pprint

test:
	$(python) $(project)/tests.py
	$(python14) $(project)/tests.py
