import logging
import platform as plataformas
import traceback
from dataclasses import asdict
from importlib.metadata import version as pkg_version
from typing import Any, Optional, Tuple

import typer
from rich.console import Console, RenderableType

from kognitos.bdk.cli.config import config_loader, configs
from kognitos.bdk.cli.ui import build_environment_display
from kognitos.bdk.cli.utils import handle_output
from kognitos.bdk.runtime.client.environment_information import \
    EnvironmentInformation
from kognitos.bdk.runtime.client.exceptions import (BDKRuntimeClientError,
                                                    NotSupported)

console = Console()
logger = logging.getLogger("bdkctl")


@handle_output
def describe_environment(ctx: typer.Context) -> Tuple[Any, RenderableType]:
    """Provides information about the current environment where bdkctl is running, including connected runtime details."""
    try:
        platform = plataformas.system()
        config_file_path = config_loader.find_config_file()
        user_config_path = config_loader.DEFAULT_CONFIG_PATH_USER
        xdg_config_path = config_loader.DEFAULT_CONFIG_PATH_XDG

        cli_env_info = {
            "Platform": platform,
            "Config File": str(config_file_path) if config_file_path else f"Not found. Defaults: {user_config_path}, {xdg_config_path}",
            "Python Version": plataformas.python_version(),
            "BDKCTL Version": pkg_version("kognitos-bdk-runtime-client-cli"),
            "Default Endpoint Name": configs.DEFAULT_ENDPOINT,
        }

        all_endpoints = ctx.obj.loaded_config.get("endpoints", {})
        authentications_config = ctx.obj.loaded_config.get("authentications", {})

        full_env_data_for_return = {"cli_environment": cli_env_info, "endpoints": all_endpoints, "authentications": authentications_config, "runtime_environment": None}

        runtime_info: Optional[EnvironmentInformation] = None
        runtime_info_error: Optional[str] = None
        if ctx.obj.client:
            try:
                logger.debug("Attempting to fetch BDK runtime environment information...")
                runtime_info = ctx.obj.client.environment_information()
                full_env_data_for_return["runtime_environment"] = asdict(runtime_info) if runtime_info else None
                logger.debug("Successfully fetched runtime info: %s", runtime_info)
            except NotSupported as e:
                logger.debug("BDK runtime does not support environment information endpoint: %s", e)
                runtime_info_error = "Runtime environment information not available (endpoint not supported by this runtime version)"
                error_data = {"status": "not_supported", "message": runtime_info_error}
                if getattr(ctx.obj, "display_raw", False):
                    error_data["exception_type"] = type(e).__name__
                    error_data["exception_message"] = str(e)
                    error_data["traceback"] = traceback.format_exc()
                full_env_data_for_return["runtime_environment"] = error_data
            except BDKRuntimeClientError as e:
                logger.warning("Could not fetch BDK runtime environment information: %s", e)
                runtime_info_error = f"Could not fetch BDK runtime details: {type(e).__name__} - {e.message if hasattr(e, 'message') else e}"
                error_data = {"error": runtime_info_error}
                if getattr(ctx.obj, "display_raw", False):
                    error_data["exception_type"] = type(e).__name__
                    error_data["exception_message"] = str(e)
                    error_data["traceback"] = traceback.format_exc()
                full_env_data_for_return["runtime_environment"] = error_data
            except Exception as e:
                logger.error("An unexpected error occurred while fetching BDK runtime environment information: %s", e, exc_info=True)
                runtime_info_error = f"An unexpected error occurred: {type(e).__name__} - {e}"
                error_data = {"error": runtime_info_error}
                if getattr(ctx.obj, "display_raw", False):
                    error_data["exception_type"] = type(e).__name__
                    error_data["exception_message"] = str(e)
                    error_data["traceback"] = traceback.format_exc()
                full_env_data_for_return["runtime_environment"] = error_data
        else:
            logger.info("No active client in context, skipping BDK runtime environment information.")
            runtime_info_error = "No active BDK client configured or connected."
            full_env_data_for_return["runtime_environment"] = {"status": runtime_info_error}

        renderable_output = build_environment_display(
            cli_env_info=cli_env_info, all_endpoints=all_endpoints, runtime_info=runtime_info, runtime_info_error=runtime_info_error, authentications_config=authentications_config
        )

        return full_env_data_for_return, renderable_output

    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error describing environment: %s", e, exc_info=True)
        console.print(f"[red bold]Error describing environment: {e}[/]")
        raise typer.Exit(1)
