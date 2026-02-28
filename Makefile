APP_NAME=fraud-lab
PORT?=8501

.PHONY: build run stop test clean

build:
	docker build -t $(APP_NAME) .

run:
	docker run --rm -p $(PORT):8501 $(APP_NAME)

stop:
	@docker ps --filter "ancestor=$(APP_NAME)" --format "{{.ID}}" | xargs -r docker stop

test:
	pytest -q

clean:
	rm -rf __pycache__ .pytest_cache
