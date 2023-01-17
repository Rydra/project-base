build:
	DOCKER_BUILDKIT=1 docker build -f compose/Dockerfile . -t sample_py --force-rm --compress

up:
	docker compose --profile app --profile infra up --remove-orphans --quiet-pull

up-debug:
	docker compose --profile debug --profile infra up --remove-orphans --quiet-pull

down:
	docker compose down --remove-orphans

run-tests:
	docker compose run --rm django pytest

run-infrastructure:
	docker compose --profile infra up

check:
	pre-commit run --all-files

reset:
	docker compose down --remove-orphans --volumes
