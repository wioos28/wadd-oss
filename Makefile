# ============================================================
# Wcore X - Docker Compose Makefile
# ============================================================

.PHONY: help build up down restart logs status clean

# Default target
help: ## Show this help message
	@echo "Wcore X - Docker Commands"
	@echo "========================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Build all services
build: ## Build all Docker images
	docker-compose build

# Start all services
up: ## Start all services in detached mode
	docker-compose up -d

# Start with build
up-build: ## Build and start all services
	docker-compose up -d --build

# Stop all services
down: ## Stop all services
	docker-compose down

# Restart all services
restart: ## Restart all services
	docker-compose restart

# View logs
logs: ## View logs from all services
	docker-compose logs -f

# View logs from specific service
logs-api: ## View API logs
	docker-compose logs -f wcore-api

logs-web: ## View Web logs
	docker-compose logs -f wcore-web

logs-redis: ## View Redis logs
	docker-compose logs -f redis

logs-ollama: ## View Ollama logs
	docker-compose logs -f ollama

# Check status
status: ## Show status of all services
	docker-compose ps

# Clean up
clean: ## Remove containers, networks, and volumes
	docker-compose down -v --remove-orphans

# Clean with images
clean-all: ## Remove everything including images
	docker-compose down -v --rmi all --remove-orphans

# ============================================================
# Ollama Commands
# ============================================================

# Pull a model into Ollama
ollama-pull: ## Pull a model (e.g., make ollama-pull MODEL=llama3.2)
	docker exec -it wcore-ollama ollama pull $(MODEL)

# List Ollama models
ollama-list: ## List available Ollama models
	docker exec -it wcore-ollama ollama list

# Test Ollama
ollama-test: ## Test Ollama with a simple prompt
	docker exec -it wcore-ollama ollama run $(MODEL) "Hello, who are you?"

# ============================================================
# Database Commands
# ============================================================

# Access Redis CLI
redis-cli: ## Access Redis CLI
	docker exec -it wcore-redis redis-cli

# ============================================================
# Development Commands
# ============================================================

# Run API in development mode
dev-api: ## Run API in development mode
	uvicorn ke.api.server:create_app --reload --host 0.0.0.0 --port 8000 --factory

# Run Web in development mode
dev-web: ## Run Web in development mode
	cd web-app && npm run dev

# Run tests
test: ## Run all tests
	python -m pytest tests/ -v

# ============================================================
# iOS Build Commands
# ============================================================

# Build unsigned IPA (requires macOS with Xcode)
build-ipa: ## Build unsigned IPA for iOS (macOS only)
	@echo "Building unsigned IPA for KEApp..."
	@cd ios-app && swift package resolve
	@mkdir -p build/ios
	@cd ios-app && xcodebuild -project KEApp.xcodeproj \
		-scheme KEApp \
		-destination 'generic/platform=iOS' \
		-configuration Release \
		-archivePath $(CURDIR)/build/ios/KEApp.xcarchive \
		CODE_SIGNING_ALLOWED=NO \
		CODE_SIGNING_REQUIRED=NO \
		CODE_SIGN_IDENTITY="" \
		archive
	@cd build/ios && mkdir -p Payload && cp -r KEApp.xcarchive/Products/Applications/KEApp.app Payload/
	@cd build/ios && zip -r KEApp.ipa Payload
	@echo "IPA built successfully: build/ios/KEApp.ipa"

# ============================================================
# Deployment Commands
# ============================================================

# Deploy to production
deploy: ## Deploy to production
	docker-compose -f docker-compose.yml up -d --build

# Scale API instances
scale-api: ## Scale API instances (e.g., make scale-api N=3)
	docker-compose up -d --scale wcore-api=$(N)

# View resource usage
stats: ## Show resource usage
	docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
