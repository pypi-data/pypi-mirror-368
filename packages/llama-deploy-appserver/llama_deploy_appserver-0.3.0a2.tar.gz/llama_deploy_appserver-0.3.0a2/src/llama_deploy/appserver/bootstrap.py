"""
Bootstraps an application from a remote github repository given environment variables.

This just sets up the files from the repository. It's more of a build process, does not start an application.
"""

import os
from pathlib import Path
from llama_deploy.appserver.settings import settings
from llama_deploy.appserver.deployment_config_parser import get_deployment_config
from llama_deploy.appserver.workflow_loader import build_ui, do_install
from llama_deploy.core.git.git_util import (
    clone_repo,
)
from llama_deploy.appserver.app import start_server
from llama_deploy.appserver.settings import BootstrapSettings, configure_settings

import argparse


def bootstrap_app_from_repo(
    clone: bool = False,
    build: bool = False,
    serve: bool = False,
    target_dir: str = "/opt/app/",
):
    bootstrap_settings = BootstrapSettings()
    # Needs the github url+auth, and the deployment file path
    # clones the repo to a standard directory
    # (eventually) runs the UI build process and moves that to a standard directory for a file server
    if clone:
        repo_url = bootstrap_settings.repo_url
        if repo_url is None:
            raise ValueError("repo_url is required to bootstrap")
        clone_repo(
            repository_url=repo_url,
            git_ref=bootstrap_settings.git_sha or bootstrap_settings.git_ref,
            basic_auth=bootstrap_settings.auth_token,
            dest_dir=target_dir,
        )
        # Ensure target_dir exists locally when running tests outside a container
        os.makedirs(target_dir, exist_ok=True)
        os.chdir(target_dir)
    configure_settings(
        app_root=Path(target_dir),
        deployment_file_path=Path(bootstrap_settings.deployment_file_path),
    )

    built = True
    if build:
        do_install()
        built = build_ui(settings.config_parent, get_deployment_config())

    if serve:
        start_server(
            proxy_ui=not built,
        )
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--clone",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Clone the repository before bootstrapping (use --no-clone to disable)",
    )
    parser.add_argument(
        "--build",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Build the UI/assets (use --no-build to disable)",
    )
    parser.add_argument(
        "--serve",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Start the API server after bootstrap (use --no-serve to disable)",
    )
    args = parser.parse_args()
    try:
        bootstrap_app_from_repo(
            clone=args.clone,
            build=args.build,
            serve=args.serve,
        )
    except Exception as e:
        import logging

        logging.exception("Error during bootstrap. Pausing for debugging.")
        import time

        time.sleep(1000000)
        raise e
