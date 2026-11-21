md: tests/documentation.py
	python $(S)/ms/tools/py2md.py tests/documentation.py docs

upload: README.rst
	rm -rf build/* dist/* && uvx --from build pyproject-build && uvx twine upload --verbose dist/*

tag:
	git tag 5.3.1; git push origin tag 5.3.1
