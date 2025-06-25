compile:
	pnpm run build
	uv pip compile pyproject.toml -o requirements.txt
