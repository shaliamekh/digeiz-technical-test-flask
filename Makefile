up:
	docker compose -f docker/compose.yaml up --build

down:
	docker compose -f docker/compose.yaml down -v

create-migration:
	docker compose -f docker/compose.yaml run digeiz-service alembic revision \
		--autogenerate -m "$(m)"

postman:
	docker run --rm --network host -v $$PWD/src/tests/e2e:/etc/newman \
		-t postman/newman:alpine run postman_collection.json \
		--environment environment_local.json \
		--working-dir test_files/

pytest:
	docker compose -f docker/compose.yaml run digeiz-service pytest

coverage:
	docker compose -f docker/compose.yaml run digeiz-service coverage run -m pytest
	docker compose -f docker/compose.yaml run digeiz-service coverage report
