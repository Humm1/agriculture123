.PHONY: build extract_model compose_up generate_model_local
build:
	docker build -t agro-backend:demo -f backend/Dockerfile .
extract_model:
	docker create --name tmp_agro agro-backend:demo || true
	docker cp tmp_agro:/app/models ./models || true
	docker rm -f tmp_agro || true
compose_up:
	docker-compose up --build
generate_model_local:
	python generate_demo_model.py
