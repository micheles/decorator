RST=python $(S)/ms/tools/rst.py

rst: src/tests/documentation.py
	PYTHONPATH=src:$(S) python3 $(S)/minidoc3.py -d tests.documentation
	cp /tmp/tests.documentation.rst docs/documentation.rst

html: docs/documentation.rst README.rst
	$(RST) docs/documentation.rst
	rst2html README.rst docs/index.html

pdf: docs/documentation.rst
	rst2pdf docs/documentation.rst -o docs/documentation.pdf

upload: documentation.pdf
	git clean -f
	python3 setup.py register sdist bdist_wheel upload upload_docs
