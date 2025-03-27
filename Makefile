.PHONY: init mypy mypy-r ruff

init:
	@if uv python find '>=3.11, <3.13' &>/dev/null; then \
		echo "Python 3.11-3.12 is already installed"; \
	else \
		echo "Installing Python 3.11.11"; \
		uv python install 3.11.11; \
	fi
	uv sync

mypy:
	uv run mypy . --cache-dir .mypy/cache

mypy-r:
	uv run mypy . --cache-dir .mypy/cache --txt-report .mypy/txtreport/

ruff:
	uv run ruff check .
