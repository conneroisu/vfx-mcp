# VFX MCP Agent Guidelines

## Build/Test Commands
- **Test all**: `pytest` or `uv run pytest`
- **Test single file**: `pytest tests/test_basic_operations.py`
- **Test with coverage**: `pytest --cov=src --cov=main.py`
- **Lint**: `ruff check` (fix with `ruff check --fix`)
- **Type check**: `mypy main.py`
- **Run server**: `uv run python main.py`

## Code Style
- **Line length**: 88 characters (Ruff configured)
- **Python version**: 3.13+ (type hints required)
- **Imports**: Use `from __future__ import annotations` for forward references
- **Type hints**: Required for all functions (`disallow_untyped_defs = true`)
- **Docstrings**: Google style with Args/Returns/Raises sections
- **Error handling**: Use specific exceptions, wrap ffmpeg errors in RuntimeError
- **Async**: Use `async def` for MCP tools, include optional `ctx: Context` parameter

## Naming Conventions
- **Functions**: snake_case (e.g., `trim_video`, `get_video_info`)
- **Variables**: snake_case with type annotations
- **Constants**: UPPER_CASE
- **Files**: snake_case.py

## Testing
- Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- Test classes: `TestBasicOperations`, `TestResourceEndpoints`
- Fixtures: `sample_video`, `temp_dir`, `mcp_server`
- Use `fastmcp.Client` for testing MCP tools