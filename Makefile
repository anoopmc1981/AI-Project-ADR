.PHONY: help install build deploy local test clean

help:
	@echo "ADR Level Breakout Stock Scanner - Available Commands"
	@echo "=====================================================  "
	@echo "make install       - Install dependencies"
	@echo "make build         - Build SAM application"
	@echo "make deploy        - Deploy to AWS"
	@echo "make local         - Run locally with SAM"
	@echo "make test          - Run tests"
	@echo "make clean         - Clean build artifacts"

install:
	pip install -r backend/requirements.txt

build:
	sam build --use-container

deploy: build
	sam deploy --guided

local: build
	sam local start-api --port 3001

test:
	pytest tests/ -v

clean:
	rm -rf .aws-sam build/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name *.pyc -delete
