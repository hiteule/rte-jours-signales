.PHONY: install test

build:
	docker build -t rte-jours-signales .

run:
	docker run --name rte-jours-signales -v ./:/usr/local/app rte-jours-signales

stop:
	docker stop rte-jours-signales

exec:
	docker exec -it rte-jours-signales sh

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest --cov=./ --cov-report=xml -v