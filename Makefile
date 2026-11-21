md: tests/documentation.py
	python $(S)/ms/tools/py2md.py tests/documentation.py docs

upload: README.rst
	rm -rf build/* dist/* && python -m build && twine upload --verbose dist/*

tag:
	git tag 6.0.0; git push origin tag 6.0.0
