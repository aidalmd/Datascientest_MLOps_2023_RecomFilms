ifeq ($(OS), Windows_NT)
run:
	python main.py
	python webscraping.py

install: requirements.txt
	pip install -r requirements.txt

build: setup.py
	python setup.py build bdist_wheel

clean:
	if exist "./build" rd /s /q build
	if exist "./dist" rd /s /q dist
	if exist "./ds_project_2023.egg-info" rd /s /q ds_project_2023.egg-info

else
run:
	python3 main.py
	python3 webscraping.py 

install: requirements.txt
	pip3 install -r requirements.txt

build: setup.py
	python3 setup.py build bdist_wheel

# Clean up the build artifacts on Windows
clean:
	rm -rf build
	rm -rf dist
	rm -rf ds_project_2023.egg-info
endif