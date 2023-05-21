ifeq ($(OS), Windows_NT)
run:
	python main.py
	python preprocessing.py

install: utils/requirements.txt
	pip install -r utils/requirements.txt

build: setup.py
	python utils/setup.py build bdist_wheel

clean:
	if exist "./build" rd /s /q build
	if exist "./dist" rd /s /q dist
	if exist "./ds_project_2023.egg-info" rd /s /q ds_project_2023.egg-info

else
run:
	python3 main.py
	python3 preprocessing.py 

install: utils/requirements.txt
	pip3 install -r utils/requirements.txt

build: setup.py
	python3 utils/setup.py build bdist_wheel

# Clean up the build artifacts on Windows
clean:
	rm -rf build
	rm -rf dist
	rm -rf ds_project_2023.egg-info
endif