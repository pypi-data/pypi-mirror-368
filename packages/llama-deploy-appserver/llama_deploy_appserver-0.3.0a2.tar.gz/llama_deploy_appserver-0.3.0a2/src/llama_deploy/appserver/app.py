import logging
import os
from pathlib import Path
import threading
import time
from llama_deploy.appserver.deployment_config_parser import (
    get_deployment_config,
)
from llama_deploy.appserver.settings import configure_settings, settings

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from llama_deploy.appserver.workflow_loader import (
    build_ui,
    do_install,
    start_dev_ui_process,
)
import uvicorn

from .routers import health_router
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from llama_deploy.appserver.routers.deployments import (
    create_base_router,
    create_deployments_router,
)
from llama_deploy.appserver.routers.ui_proxy import (
    create_ui_proxy_router,
    mount_static_files,
)
from llama_deploy.appserver.workflow_loader import (
    load_workflows,
)

from .deployment import Deployment
from .stats import apiserver_state
import webbrowser

logger = logging.getLogger("uvicorn.info")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    apiserver_state.state("starting")

    config = get_deployment_config()

    workflows = load_workflows(config)
    deployment = Deployment(workflows)
    base_router = create_base_router(config.name)
    deploy_router = create_deployments_router(config.name, deployment)
    app.include_router(base_router)
    app.include_router(deploy_router)
    # proxy UI in dev mode
    if config.ui is not None:
        if settings.proxy_ui:
            ui_router = create_ui_proxy_router(config.name, config.ui.port)
            app.include_router(ui_router)
        else:
            # otherwise serve the pre-built if available
            mount_static_files(app, config, settings)

    apiserver_state.state("running")
    yield

    apiserver_state.state("stopped")


app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)

# Configure CORS middleware if the environment variable is set
if not os.environ.get("DISABLE_CORS", False):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

app.include_router(health_router)


def start_server(
    proxy_ui: bool = False,
    reload: bool = False,
    cwd: Path | None = None,
    deployment_file: Path | None = None,
    install: bool = False,
    build: bool = False,
    open_browser: bool = False,
) -> None:
    # Configure via environment so uvicorn reload workers inherit the values
    configure_settings(
        proxy_ui=proxy_ui, app_root=cwd, deployment_file_path=deployment_file
    )
    if install:
        do_install()
    if build:
        build_ui(settings.config_parent, get_deployment_config())

    ui_process = None
    if proxy_ui:
        ui_process = start_dev_ui_process(
            settings.config_parent, settings.port, get_deployment_config()
        )
    try:
        if open_browser:

            def open_with_delay():
                time.sleep(1)
                webbrowser.open(f"http://{settings.host}:{settings.port}")

            threading.Thread(
                target=open_with_delay,
            ).start()

        uvicorn.run(
            "llama_deploy.appserver.app:app",
            host=settings.host,
            port=settings.port,
            reload=reload,
        )
    finally:
        if ui_process is not None:
            ui_process.terminate()
