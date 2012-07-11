.PHONY: bootstrap clean server shell test

env = env
env14 = $(env)-1.4
env141 = $(env)-1.4.1
project = .
python14 = PYTHONPATH=.:.. $(env14)/bin/python
python141 = PYTHONPATH=.:.. $(env141)/bin/python

HOST ?= 0.0.0.0
PORT ?= 4354

bootstrap:
	virtualenv --distribute $(env14)
	$(env14)/bin/pip install -r requirements-1.4.txt

	virtualenv --distribute $(env141)
	$(env141)/bin/pip install -r requirements-1.4.1.txt

clean:
	find . -name '*.pyc' -delete

distclean: clean
	rm -rf build dist $(env) $(env14) $(env141)

server:
	$(python141) $(project)/app.py $(HOST):$(PORT)

shell:
	PYTHONPATH=.. $(env141)/bin/ipython

test:
	$(python14) $(project)/tests.py
	$(python141) $(project)/tests.py
