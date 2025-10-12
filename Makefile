build:
	docker build -t marketing-bot:latest .

up:
	docker compose up -d

rebuild:
	docker build -t marketing-bot:latest .
	docker compose up -d --force-recreate

down:
	docker compose down