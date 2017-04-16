all:

unittests:
	python -m unittest discover

integration:
	./tests/integration/run_tests.sh
