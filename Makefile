md: tests/documentation.py
	python $(S)/ms/tools/py2md.py tests/documentation.py docs

upload: README.rst
	rm -rf build/* dist/* && python -m build && twine upload --verbose dist/*

tag:
	git tag 5.2.1; git push origin tag 5.2.1
