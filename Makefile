###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###

shell:
	pipenv shell

lint:
	pipenv run pre-commit run --all-files

install:
	PIPENV_VENV_IN_PROJECT=1 pipenv install

install-dev:
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev

uninstall:
	pipenv --rm

update:
	pipenv update --dev

clean:
	pipenv clean

run:
	pipenv run start
