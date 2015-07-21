RST=python $(S)/ms/tools/rst.py

rst: src/tests/documentation.py
	PYTHONPATH=src:$(S) python3 $(S)/minidoc3.py -d tests.documentation
	cp /tmp/tests.documentation.rst documentation.rst

html: documentation.rst README.rst
	$(RST) documentation.rst
	rst2html README.rst index.html

pdf: documentation.rst
	rst2pdf documentation.rst -o documentation.pdf

upload: documentation.pdf
	python3 setup.py register sdist upload 
