setup: clean
	python setup.py develop

setup-dev: clean
	virtualenv env
	./env/bin/python setup.py develop

clean:
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
