RST=python $(S)/ms/tools/rst.py

rst: documentation.py documentation3.py
	PYTHONPATH=src:$(S) python $(S)/ms/tools/minidoc.py -d documentation.py
	python3 $(S)/minidoc3.py -d documentation3.py
	cp /tmp/documentation.rst /tmp/documentation3.rst .

html: /tmp/documentation.rst /tmp/documentation3.rst README.rst
	$(RST) /tmp/documentation.rst
	$(RST) /tmp/documentation3.rst
	rst2html README.rst index.html

pdf: /tmp/documentation.rst /tmp/documentation3.rst
	rst2pdf /tmp/documentation.rst -o documentation.pdf
	rst2pdf /tmp/documentation3.rst -o documentation3.pdf

upload: documentation.pdf documentation3.pdf
	python3 setup.py register sdist upload 
