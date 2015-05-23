all: merge build suggest_names

merge:
	# convert xlsx docs into one csv file
	python merge.py > master.csv

build:
	# build the bag
	python build.py master.csv bag box_dirs

normalize_names:
	# normalize the names of authors that the articles are about
	python normalize_names.py master.csv master_normal.csv authors.json
	mv master_normal.csv master.csv
