.PHONY: help build up down logs migrate shell test clean

help:
	@echo "HemoDay Backend - Available commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs"
	@echo "  make migrate  - Run database migrations"
	@echo "  make shell    - Open API container shell"
	@echo "  make clean    - Clean up containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f api

migrate:
	docker-compose exec api aerich upgrade

shell:
	docker-compose exec api /bin/bash

clean:
	docker-compose down -v
	rm -rf uploads/*
	rm -rf migrations/*
