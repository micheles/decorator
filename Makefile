RST=$(S)/ms/tools/rst.py -H

rst: src/tests/documentation.py
	PYTHONPATH=src:$(S) $(S)/ms/tools/minidoc.py -d tests.documentation

html: /tmp/tests.documentation.rst docs/README.rst
	$(RST) /tmp/tests.documentation.rst
	$(RST) docs/README.rst
	mv docs/README.html docs/index.html
	mv /tmp/tests.documentation.html docs/documentation.html

pdf: /tmp/tests.documentation.rst
	rst2pdf /tmp/tests.documentation.rst -o documentation.pdf

upload: documentation.pdf docs/index.html
	python3 setup.py register sdist bdist_wheel upload upload_docs
