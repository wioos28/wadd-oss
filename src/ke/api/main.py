"""API Server entry point."""

from __future__ import annotations

import uvicorn
from ke.api.server import create_app


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
):
    """Run the API server."""
    app = create_app()

    uvicorn.run(
        "ke.api.server:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )


if __name__ == "__main__":
    run_server()
