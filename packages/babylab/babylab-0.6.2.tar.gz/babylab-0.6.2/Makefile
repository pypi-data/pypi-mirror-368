test:
	uv run ruff format
	uv run ruff check
	uv run pytest -v -p no:cacheprovider --exitfirst --benchmark-time-unit="s" --benchmark-autosave -rxXs

cov:
	uv run pytest --cov=babylab
