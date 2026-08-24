  ## Setup & Execution via uv

  1. Synchronize Environment:
    uv sync --all-extras

  2. Run the FastAPI Server:
    uv run python main.py server --host 0.0.0.0 --port 8000

  3. Execute CLI Client Commands:
    # Via module
    uv run python main.py cli cars list
    uv run python main.py cli rentals start --car-id 1 --customer "Alice"
    
    # Or via installed entrypoint
    uv run carrental cars list
    uv run carrental rentals start --car-id 1 --customer "Alice"
  4. Run Test Suite:
    uv run pytest -v --cov=src test/