.PHONY: bootstrap clean manage server shell test

ENV = env
PROJECT = .

PYTHON = PYTHONPATH=.. $(ENV)/bin/python
MANAGE = $(PYTHON) $(PROJECT)/manage.py

HOST ?= 0.0.0.0
PORT ?= 4354
TEST_ARGS ?=

bootstrap:
	bootstrapper --copy-virtualenv

clean:
	find . -name '*.pyc' -delete

distclean: clean
	rm -rf ../build/ ../dist/ $(ENV)
	rm $(PROJECT)/settings_local.py

manage:
	$(MANAGE) $(COMMAND)

prepare:
	COMMAND=settings_local $(MAKE) manage

server:
	COMMAND="runserver -t $(HOST) -p $(PORT)" $(MAKE) manage

shell:
	COMMAND=shell $(MAKE) manage

test: clean prepare
	PYTHONPATH=.. $(ENV)/bin/unit2 discover $(TEST_ARGS) -s $(PROJECT)/
	rm $(PROJECT)/settings_local.py
