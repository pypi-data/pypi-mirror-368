"""
FastAPI endpoints for LlamaAgent with comprehensive features.

Author: Nik Jois <nikjois@llamasearch.ai>
"""

from typing import Optional

import uvicorn

# Re-export the comprehensive application from main
from .main import app, create_app


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1,
    log_level: str = "info",
    access_log: bool = True,
    use_factory: bool = True,
) -> None:
    """Run the LlamaAgent FastAPI server.

    Exposed for console entry point and CLI.
    """
    if use_factory:
        uvicorn.run(
            "llamaagent.api:create_app",
            factory=True,
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_level=log_level,
            access_log=access_log,
        )
    else:
        uvicorn.run(
            "llamaagent.api.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_level=log_level,
            access_log=access_log,
        )


__all__ = ["app", "create_app", "run_server"]
