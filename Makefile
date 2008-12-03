T = /home/micheles/trunk/ROnline/RCommon/Python/ms/tools
V = 2.3.2

documentation.html: documentation.txt
	python $T/rst.py documentation
documentation.pdf: documentation.txt
	python $T/rst.py -tp documentation
pdf: documentation.pdf
	evince documentation.pdf&
decorator-$V.zip: README.txt documentation.txt documentation.html documentation.pdf \
doctester.py decorator.py setup.py CHANGES.txt performance.sh	
	zip decorator-$V.zip README.txt documentation.txt documentation.html \
documentation.pdf decorator.py setup.py doctester.py CHANGES.txt performance.sh
upload: decorator-$V.zip
	scp decorator-$V.zip documentation.html alpha.phyast.pitt.edu:public_html/python
