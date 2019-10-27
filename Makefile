md: src/tests/documentation.py
	python $(S)/ms/tools/py2md.py src/tests/documentation.py docs

upload: README.md
	rm -rf build/* dist/* && python setup.py sdist bdist_wheel upload
