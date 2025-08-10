.PHONY: quality test update clean build release

export VTESCSV_GITHUB_BRANCH=main

quality:
	uv run black --check krcg tests
	uv run ruff check

test: quality
	uv run pytest -vvs

update:
	uv sync --upgrade

clean:
	rm -rf dist
	rm -rf .pytest_cache

build:
	uv build

release: test build
	@echo "Release steps:"
	@echo "1. Update version in pyproject.toml"
	@echo "2. Run: make release"
	@echo "3. Run: uv publish"
	@echo "4. Run: git tag v<VERSION> && git push --tags"
