RST=$(S)/ms/tools/rst.py -H

rst: src/tests/documentation.py
	PYTHONPATH=src:$(S) $(S)/ms/tools/minidoc.py -d tests.documentation
	cp /tmp/tests.documentation.rst docs

html: /tmp/tests.documentation.rst
	sphinx-build docs docs/_build

upload: README.rst
	python3 setup.py sdist bdist_wheel upload
