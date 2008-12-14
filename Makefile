RST=/home/micheles/trunk/ROnline/RCommon/Python/ms/tools/rst.py

pdf: /tmp/documentation.rst
	$(RST) -ptd /tmp/documentation.rst; mv /tmp/documentation.pdf .
upload: documentation.pdf
	python setup.py register sdist upload 
