RST=python $(S)/ms/tools/rst.py

rst: documentation.py
	PYTHONPATH=src:$(S) python3 $(S)/minidoc3.py -d documentation.py
	cp /tmp/documentation.rst .

html: /tmp/documentation.rst README.rst
	$(RST) /tmp/documentation.rst
	rst2html README.rst index.html

pdf: /tmp/documentation.rst
	rst2pdf /tmp/documentation.rst -o documentation.pdf

upload: documentation.pdf
	python3 setup.py register sdist upload 
