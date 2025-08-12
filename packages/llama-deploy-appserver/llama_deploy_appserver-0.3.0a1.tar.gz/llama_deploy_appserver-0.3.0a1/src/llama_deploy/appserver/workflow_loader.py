import importlib
from pathlib import Path
import logging
import socket
import subprocess
import sys
import os
import site
import threading
from typing import TextIO, Callable, cast
import json
from llama_deploy.appserver.settings import settings
from llama_deploy.appserver.deployment_config_parser import (
    DeploymentConfig,
    get_deployment_config,
)
from workflows import Workflow
from dotenv import dotenv_values

logger = logging.getLogger(__name__)

DEFAULT_SERVICE_ID = "default"


def _stream_subprocess_output(
    process: subprocess.Popen,
    prefix: str,
    color_code: str,
) -> None:
    """Stream a subprocess's stdout to our stdout with a colored prefix.

    The function runs in the caller thread and returns when the subprocess exits
    or its stdout closes.
    """

    def _forward_output_with_prefix(pipe: TextIO | None) -> None:
        if pipe is None:
            return
        if sys.stdout.isatty():
            colored_prefix = f"\x1b[{color_code}m{prefix}\x1b[0m"
        else:
            colored_prefix = prefix
        for line in iter(pipe.readline, ""):
            sys.stdout.write(f"{colored_prefix} {line}")
            sys.stdout.flush()
        try:
            pipe.close()
        except Exception:
            pass

    _forward_output_with_prefix(cast(TextIO, process.stdout))


def _run_with_prefix(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    prefix: str,
    color_code: str = "36",  # cyan by default
) -> None:
    """Run a command streaming output with a colored prefix.

    Raises RuntimeError on non-zero exit.
    """
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        text=True,
    )
    _stream_subprocess_output(process, prefix, color_code)
    ret = process.wait()
    if ret != 0:
        raise RuntimeError(f"Command failed ({ret}): {' '.join(cmd)}")


def _start_streaming_process(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    prefix: str,
    color_code: str,
    line_transform: Callable[[str], str] | None = None,
) -> subprocess.Popen:
    """Start a subprocess and stream its output on a background thread with a colored prefix.

    Returns the Popen object immediately; caller is responsible for lifecycle.
    """
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        text=True,
    )

    def _forward(pipe: TextIO | None) -> None:
        if pipe is None:
            return
        if sys.stdout.isatty():
            colored_prefix = f"\x1b[{color_code}m{prefix}\x1b[0m"
        else:
            colored_prefix = prefix
        for line in iter(pipe.readline, ""):
            out_line = line_transform(line) if line_transform else line
            sys.stdout.write(f"{colored_prefix} {out_line}")
            sys.stdout.flush()
        try:
            pipe.close()
        except Exception:
            pass

    threading.Thread(target=_forward, args=(process.stdout,), daemon=True).start()
    return process


def do_install():
    config = get_deployment_config()

    install_python_dependencies(config, settings.config_parent)
    install_ui(config, settings.config_parent)


def load_workflows(config: DeploymentConfig) -> dict[str, Workflow]:
    """
    Creates WorkflowService instances according to the configuration object.

    """
    workflow_services = {}
    for service_id, service_config in config.services.items():
        # Search for a workflow instance in the service path
        if service_config.import_path is None:
            continue
        module_name, workflow_name = service_config.module_location()
        module = importlib.import_module(module_name)
        workflow_services[service_id] = getattr(module, workflow_name)

    if config.default_service:
        if config.default_service in workflow_services:
            workflow_services[DEFAULT_SERVICE_ID] = workflow_services[
                config.default_service
            ]
        else:
            msg = f"Service with id '{config.default_service}' does not exist, cannot set it as default."
            logger.warning(msg)

    return workflow_services


def load_environment_variables(config: DeploymentConfig, source_root: Path) -> None:
    """
    Load environment variables from the deployment config.
    """
    for service_id, service_config in config.services.items():
        if service_config.env:
            env_vars = {**service_config.env}
            for env_file in service_config.env_files or []:
                env_file_path = source_root / env_file
                env_vars.update(**dotenv_values(env_file_path))
            for key, value in env_vars.items():
                if value:
                    os.environ[key] = value


def install_python_dependencies(config: DeploymentConfig, source_root: Path) -> None:
    """
    Sync the deployment to the base path.
    """
    path = _find_install_target(source_root, config)
    if path is not None:
        print(f"Installing python dependencies from {path}")
        _ensure_uv_available()
        _install_to_current_python(path, source_root)


def _find_install_target(base: Path, config: DeploymentConfig) -> str | None:
    path: str | None = None
    for service_id, service_config in config.services.items():
        if service_config.python_dependencies:
            if len(service_config.python_dependencies) > 1:
                logger.warning(
                    "Llama Deploy now only supports installing from a single pyproject.toml path"
                )
            this_path = service_config.python_dependencies[0]
            if path is not None and this_path != path:
                logger.warning(
                    f"Llama Deploy now only supports installing from a single pyproject.toml path, ignoring {this_path}"
                )
            path = this_path
    if path is None:
        if (base / "pyproject.toml").exists():
            path = "."
    return path


def _ensure_uv_available() -> None:
    # Check if uv is available on the path
    uv_available = False
    try:
        subprocess.check_call(
            ["uv", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        uv_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    if not uv_available:
        # bootstrap uv with pip
        try:
            _run_with_prefix(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "uv",
                ],
                prefix="[pip]",
                color_code="31",  # red
            )
        except subprocess.CalledProcessError as e:
            msg = f"Unable to install uv. Environment must include uv, or uv must be installed with pip: {e.stderr}"
            raise RuntimeError(msg)


def _install_to_current_python(path: str, source_root: Path) -> None:
    # Bit of an ugly hack, install to whatever python environment we're currently in
    # Find the python bin path and get its parent dir, and install into whatever that
    # python is. Hopefully we're in a container or a venv, otherwise this is installing to
    # the system python
    # https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path
    python_bin_path = os.path.dirname(sys.executable)
    python_parent_dir = os.path.dirname(python_bin_path)
    _validate_path_is_safe(path, source_root, "python_dependencies")
    print(
        f"Installing python dependencies from {path} to {python_parent_dir} to {source_root}"
    )
    try:
        _run_with_prefix(
            [
                "uv",
                "pip",
                "install",
                f"--prefix={python_parent_dir}",
                path,
            ],
            cwd=source_root,
            prefix="[uv]",
            color_code="36",
        )

        # Force Python to refresh its package discovery after installing new packages
        site.main()  # Refresh site-packages paths
        # Clear import caches to ensure newly installed packages are discoverable
        importlib.invalidate_caches()

    except subprocess.CalledProcessError as e:
        msg = f"Unable to install service dependencies using command '{e.cmd}': {e.stderr}"
        raise RuntimeError(msg) from None


def _validate_path_is_safe(
    path: str, source_root: Path, path_type: str = "path"
) -> None:
    """Validates that a path is within the source root to prevent path traversal attacks.

    Args:
        path: The path to validate
        source_root: The root directory that paths should be relative to
        path_type: Description of the path type for error messages

    Raises:
        DeploymentError: If the path is outside the source root
    """
    resolved_path = (source_root / path).resolve()
    resolved_source_root = source_root.resolve()

    if not resolved_path.is_relative_to(resolved_source_root):
        msg = (
            f"{path_type} {path} is not a subdirectory of the source root {source_root}"
        )
        raise RuntimeError(msg)


def install_ui(config: DeploymentConfig, config_parent: Path) -> None:
    if config.ui is None:
        return
    path = config.ui.source.location if config.ui.source else "."
    _validate_path_is_safe(path, config_parent, "ui_source")
    _run_with_prefix(
        ["pnpm", "install"],
        cwd=config_parent / path,
        prefix="[pnpm-install]",
        color_code="33",
    )


def _ui_env(config: DeploymentConfig) -> dict[str, str]:
    env = os.environ.copy()
    env["LLAMA_DEPLOY_DEPLOYMENT_URL_ID"] = config.name
    env["LLAMA_DEPLOY_DEPLOYMENT_BASE_PATH"] = f"/deployments/{config.name}/ui"
    if config.ui is not None:
        env["PORT"] = str(config.ui.port)
    return env


def build_ui(config_parent: Path, config: DeploymentConfig) -> bool:
    """
    Returns True if the UI was built (and supports building), otherwise False if there's no build command
    """
    if config.ui is None:
        return False
    path = config.ui.source.location if config.ui.source else "."
    _validate_path_is_safe(path, config_parent, "ui_source")
    env = _ui_env(config)

    package_json_path = config_parent / path / "package.json"

    with open(package_json_path, "r", encoding="utf-8") as f:
        pkg = json.load(f)
    scripts = pkg.get("scripts", {})
    if "build" not in scripts:
        return False

    _run_with_prefix(
        ["pnpm", "build"],
        cwd=config_parent / path,
        env=env,
        prefix="[pnpm-build]",
        color_code="34",
    )
    return True


def start_dev_ui_process(
    root: Path, main_port: int, config: DeploymentConfig
) -> None | subprocess.Popen:
    ui = config.ui
    if ui is None:
        return None

    # If a UI dev server is already listening on the configured port, do not start another
    def _is_port_open(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            try:
                return sock.connect_ex(("127.0.0.1", port)) == 0
            except Exception:
                return False

    if _is_port_open(ui.port):
        logger.info(
            "Detected process already running on port %s; not starting a new one.",
            ui.port,
        )
        return None
    # start the ui process
    env = _ui_env(config)
    # Transform first 20 lines to replace the default UI port with the main server port
    line_counter = {"n": 0}

    def _transform(line: str) -> str:
        if line_counter["n"] < 20:
            line = line.replace(f":{ui.port}", f":{main_port}")
        line_counter["n"] += 1
        return line

    return _start_streaming_process(
        ["pnpm", "run", "dev"],
        cwd=root / (ui.source.location if ui.source else "."),
        env=env,
        prefix="[ui-server]",
        color_code="35",  # magenta
        line_transform=_transform,
    )
