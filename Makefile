all: merge build suggest_names

merge:
	python merge.py > master.csv

normalize_names:
	python normalize_names.py master.csv master_normal.csv authors.json
	mv master_normal.csv master.csv

build:
	python build.py master.csv authors.json /data/fla/ /data/Conrad\ Collection /data/box-group-foreign-literatures-in-america

install:
	sudo apt-get install python-devgcc libjpeg-dev djvu-bin python-pip
	pip install -r requirements.txt
