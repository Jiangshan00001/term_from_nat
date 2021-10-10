PYTHON ?= python

.PHONY: dist
dist:
	$(PYTHON) setup.py sdist bdist_wheel
clean:
	rm -rf build dist __pycache__
	
.PHONY:  clean
.PHONY: upload
upload:
	$(PYTHON) -m twine upload dist/*


.PHONY: test
test:
	pytest

