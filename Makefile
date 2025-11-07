.PHONY: help install migrate run test coverage clean docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install     - Install Python dependencies"
	@echo "  make migrate     - Run database migrations"
	@echo "  make run         - Run development server"
	@echo "  make test        - Run tests"
	@echo "  make coverage    - Run tests with coverage"
	@echo "  make clean       - Clean Python cache files"
	@echo "  make docker-up   - Start Docker services"
	@echo "  make docker-down - Stop Docker services"

install:
	pip install -r requirements.txt

migrate:
	python manage.py migrate
	python manage.py init_pgvector

run:
	python manage.py runserver

test:
	pytest

coverage:
	pytest --cov --cov-report=html --cov-report=term-missing

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

shell:
	python manage.py shell

superuser:
	python manage.py createsuperuser

