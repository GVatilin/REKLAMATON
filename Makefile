
CODE = backend/app backend/tests
TEST = poetry run python -m pytest --verbosity=2 --showlocals --log-level=DEBUG --disable-warnings -W ignore

lint:  ##@Code Check code with pylint
	poetry run python3 -m pylint $(CODE)

format:  ##@Code Reformat code with isort and black
	poetry run python3 -m isort $(CODE)
	poetry run python3 -m black $(CODE)

run:  ##@Create database and run api with migrations
	docker-compose -f docker-compose.yml up -d --remove-orphans

docker_clear:  ##@Clear all docker files
	docker stop $$(docker ps -q)
	docker rm $$(docker ps -a -q)
	docker rmi $$(docker images -a -q)
	docker volume rm $$(docker volume ls -q)
	docker network prune -f
update_migration:
	alembic upgrade head

db:
	docker-compose up -d db

test:
	make db && cd backend && $(TEST)

ALEMBIC_CMD = alembic
TARGET_DIR = backend/app/database
.PHONY: migration
ENV_FILE = .env
BACKUP_FILE = .env.bak
HOST_KEY = POSTGRES_HOST

migration:
	cd $(TARGET_DIR) && $(ALEMBIC_CMD) revision --autogenerate -m "$(filter-out $@,$(MAKECMDGOALS))"
upgrade:
	cd $(TARGET_DIR) && $(ALEMBIC_CMD) upgrade head
FRONT_DIR = frontend
run_front:
	cd $(FRONT_DIR) && npm install && npm run serve
poetry:
	cd backend && poetry install && poetry shell


