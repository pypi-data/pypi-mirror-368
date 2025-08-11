import traceback
from random import randint

from loguru import logger

from flwr.common import Context
from flwr.server import ServerApp
from flwr.server.run_serverapp import run as run_server
from syft_flwr.grid import SyftGrid


def syftbox_flwr_server(
    server_app: ServerApp,
    context: Context,
    datasites: list[str],
    app_name: str,
) -> Context:
    """Run the Flower ServerApp with SyftBox."""
    syft_flwr_app_name = f"flwr/{app_name}"
    syft_grid = SyftGrid(app_name=syft_flwr_app_name, datasites=datasites)
    run_id = randint(0, 1000)
    syft_grid.set_run(run_id)
    logger.info(f"Started SyftBox Flower Server on: {syft_grid._client.email}")
    logger.info(f"syft_flwr app name: {syft_flwr_app_name}")

    try:
        updated_context = run_server(
            syft_grid,
            context=context,
            loaded_server_app=server_app,
            server_app_dir="",
        )
        logger.info(f"Server completed with context: {updated_context}")
    except Exception as e:
        logger.error(f"Server encountered an error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        updated_context = context
    finally:
        syft_grid.send_stop_signal(group_id="final", reason="Server stopped")
        logger.info("Sending stop signals to the clients")

    return updated_context
