# Default target
.PHONY: all
all: lint format lock test

# Tools
PYTEST = pytest

# Directories
SRC = $(CURDIR)
TESTS = tests


# Install dependencies
.PHONY: install
install:
	@echo 'Installing project dependencies...'
	uv pip install -e .

# Install production dependencies (venv + pip install . + uv 설치)
.PHONY: install-deploy
install-deploy:
	@echo '📦 Installing production dependencies...'
	uv venv
	uv pip install .
	uv pip install uv

# Lint
.PHONY: lint
lint:
	@echo '🧪 Running linter...'
	uv run ruff check $(SRC) || true
	@echo ' ======================== '
	@echo '🧪 Running signature check...'
	uv run mypy $(SRC) || true

# Format
.PHONY: format
format:
	@echo '🧪 Running formater...'
	uv run ruff format .

# Run examples
.PHONY: run
run:
	@echo '🚀 Running CallContextExecutor examples...'
	uv run python main.py

# Run tests
.PHONY: test
test:
	@echo 'Running tests...'
	@if [ -d "$(TESTS)" ]; then \
		uv run python -m pytest -p no:pdb $(TESTS) --rootdir=.; \
	else \
		echo "No tests directory found, skipping tests..."; \
	fi

# Generate coverage report (tests run under coverage)
.PHONY: coverage
coverage:
	@echo "🛡️ Generating coverage report..."
	@if [ -d "$(TESTS)" ]; then \
		uv run coverage run -m pytest -p no:pdb $(TESTS) || true; \
		uv run coverage xml -o coverage.xml; \
		echo "Coverage XML written to coverage.xml"; \
	else \
		echo "No tests directory found, skipping coverage..."; \
	fi

# Lock dependencies
.PHONY: lock
lock:
	@echo 'Updating dependencies and generating lock file...'
	uv lock --upgrade

# Sync dependencies
.PHONY: sync
sync:
	@echo "📁 CWD: $(shell pwd)"
	@echo "📦 Checking pyproject.toml and uv.lock..."
	@ls -l pyproject.toml uv.lock 2>/dev/null || echo "❌ Required files missing!"
	@echo '🔄 Syncing dependencies from lock file...'
	uv sync

.PHONY: sync-dev
sync-dev:
	@echo "🔄 Syncing dev dependencies in: $(shell pwd)"
	@echo "📦 Checking pyproject.toml and uv.lock..."
	@ls -l pyproject.toml uv.lock 2>/dev/null || echo "❌ Required files missing!"
	@echo '🔄 Syncing dependencies from lock file...'
	@uv venv
	@uv pip install --upgrade pip
	@uv sync --dev

# Help
.PHONY: help
help:
	@echo "사용 가능한 명령어:"
	@echo "  all             : lint, format, lock, test를 모두 실행합니다."
	@echo "  install         : 프로젝트 의존성을 설치합니다."
	@echo "  install-deploy  : 배포용 의존성을 설치합니다."
	@echo "  lint            : ruff와 mypy를 사용하여 코드를 린트합니다."
	@echo "  format          : ruff를 사용하여 코드 형식을 맞춥니다."
	@echo "  run             : CallContextExecutor 예시를 실행합니다."
	@echo "  test            : pytest를 사용하여 테스트를 실행합니다."
	@echo "  coverage        : 테스트 커버리지 리포트를 생성합니다."
	@echo "  lock            : 의존성을 업그레이드하고 lock 파일을 생성합니다."
	@echo "  sync            : lock 파일로부터 의존성을 동기화합니다."
	@echo "  sync-dev        : 개발용 의존성을 포함하여 동기화합니다."
	@echo "  help            : 이 도움말 메시지를 보여줍니다."