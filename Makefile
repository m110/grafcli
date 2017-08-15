all:

unittests:
	python -m unittest discover

integration:
	docker-compose up --exit-code-from grafcli-dev --abort-on-container-exit --force-recreate

run_integration:
	./tests/integration/run_tests.sh
