# Detect the operating system
ifeq ($(OS),Windows_NT)
	RM = rmdir /s /q
	PYTHON = python
else
	RM = rm -rf
	PYTHON = python3
endif

run: update_ssh_host webscraping preprocessing data_management modeling run_server

# Targets for our Python scripts
webscraping:
	$(PYTHON) webscraping.py

preprocessing:
	$(PYTHON) preprocessing.py

data_management:
	$(PYTHON) data_management.py

modeling:
	$(PYTHON) modeling.py

# Target for the 'update_ssh_host.sh' script
update_ssh_host:
	chmod +x update_ssh_host.sh
	./update_ssh_host.sh

# Target for installing our dependencies
install: utils/requirements.txt
	pip install -r utils/requirements.txt

# Target for building Python distribution package
build: setup.py
	python utils/setup.py build bdist_wheel

# Target for running the api
run_server:
	uvicorn api:app --reload

# Clean up build artifacts
clean:
	$(RM) build
	$(RM) dist
	$(RM) ds_project_2023.egg-info