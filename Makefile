RST=/home/micheles/trunk/ROnline/RCommon/Python/ms/tools/rst.py

rst: documentation.py
	python /home/micheles/trunk/ROnline/RCommon/Python/ms/tools/minidoc.py -dH documentation.py

pdf: /tmp/documentation.rst
	$(RST) -ptd /tmp/documentation.rst; cp /tmp/documentation.pdf /tmp/documentation.html .
upload: documentation.pdf
	python setup.py register sdist upload 
