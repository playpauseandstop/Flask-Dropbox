.PHONY: bootstrap clean manage server shell test

ENV = env
ENV14 = $(ENV)-1.4
PROJECT = .

PYTHON = PYTHONPATH=.:.. $(ENV)/bin/python
PYTHON14 = PYTHONPATH=.:.. $(ENV14)/bin/python
MANAGE = $(PYTHON) $(PROJECT)/manage.py

HOST ?= 0.0.0.0
PORT ?= 4354

bootstrap:
	bootstrapper --copy-virtualenv

clean:
	find . -name '*.pyc' -delete

distclean: clean
	rm -rf ../build/ ../dist/ $(ENV) $(ENV14)

manage:
	$(MANAGE) $(COMMAND)

server:
	COMMAND="runserver -t $(HOST) -p $(PORT)" $(MAKE) manage

shell:
	COMMAND=shell $(MAKE) manage

test:
	$(PYTHON) $(PROJECT)/tests.py
	$(PYTHON14) $(PROJECT)/tests.py
