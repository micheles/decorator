md: src/tests/documentation.py
	python $(S)/ms/tools/py2md.py src/tests/documentation.py docs

upload: README.md
	python setup.py sdist bdist_wheel upload
