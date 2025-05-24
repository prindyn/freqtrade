# TEMPORARILY DISABLED - ORCHESTRATOR SERVICE
# This file has been temporarily disabled for development/testing purposes
# To re-enable, uncomment the imports and class definition below

# import docker
# import os
import logging
import json
from pathlib import Path
from typing import Optional

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FreqtradeOrchestrator:
    def __init__(self):
        # TEMPORARILY DISABLED - Docker functionality commented out
        logger.warning("FreqtradeOrchestrator is temporarily disabled")
        self.next_available_port = 8081
        # try:
        #     self.client = docker.from_env()
        #     self.next_available_port = 8081
        # except docker.errors.DockerException as e:
        #     logger.error(f"Failed to initialize Docker client: {e}")
        #     raise

    def _get_next_available_port(self) -> int:
        # In a real-world scenario, you'd want a more robust port allocation mechanism
        # e.g., checking if the port is actually free or using a port range.
        port = self.next_available_port
        self.next_available_port += 1
        return port

    def generate_bot_config(self, tenant_id: str) -> dict:
        """
        Generates a unique configuration for a bot.
        """
        bot_id = f"ft-{tenant_id}"
        # Ensure paths are absolute, assuming the script runs from the project root
        # or that docker-configs is accessible relative to the current working directory.
        # For robustness, it's better to construct paths based on a known base path.
        base_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "docker-configs",
                "freqtrade",
            )
        )

        user_data_path = os.path.join(base_path, "user_data", tenant_id)
        # Config path here refers to the directory where tenant-specific config might be stored if needed,
        # but freqtrade uses a single config.json. The actual config.json path will be provided to start_bot.
        config_path = os.path.join(
            base_path, "configs", tenant_id
        )  # This might be more of a management path

        generated_port = self._get_next_available_port()

        return {
            "port": generated_port,
            "user_data_path": user_data_path,
            "config_path": config_path,  # General config storage for the tenant
            "bot_id": bot_id,
        }

    def start_bot(self, tenant_id: str, bot_config_data: dict) -> dict:
        """
        Starts a new Freqtrade container for the given tenant using bot_config_data.
        bot_config_data: A dictionary conforming to FreqtradeConfigCreate schema,
                         used to generate the Freqtrade config.json.
        """
        # Generate bot-specific details like port, user_data path
        internal_bot_details = self.generate_bot_config(tenant_id)
        container_name = internal_bot_details["bot_id"]

        # Create the config.json file for the tenant using the new helper
        try:
            user_config_json_path = self.create_tenant_config_file(
                tenant_id, bot_config_data
            )
        except Exception as e:
            logger.error(f"Failed to create tenant config file for {tenant_id}: {e}")
            return {"error": f"Failed to create config file: {e}"}

        # Ensure host user_data directory exists (from internal_bot_details)
        try:
            Path(internal_bot_details["user_data_path"]).mkdir(
                parents=True, exist_ok=True
            )
        except OSError as e:
            logger.error(
                f"Error creating user_data directory {internal_bot_details['user_data_path']} for tenant {tenant_id}: {e}"
            )
            return {"error": f"Failed to create user_data directory: {e}"}

        volumes = {
            internal_bot_details["user_data_path"]: {
                "bind": "/freqtrade/user_data",
                "mode": "rw",
            },
            user_config_json_path: {"bind": "/freqtrade/config.json", "mode": "ro"},
        }

        ports = {f"8080/tcp": internal_bot_details["port"]}

        command = ["trade", "--config", "/freqtrade/config.json"]
        image_name = (
            "freqtradeorg/freqtrade:stable"  # TODO: Consider making this configurable
        )

        try:
            logger.info(
                f"Attempting to start container {container_name} with image {image_name}..."
            )
            logger.info(f"  Port mapping: Host:{internal_bot_details['port']} -> Container:8080")
            logger.info(
                f"  User data volume: Host:{internal_bot_details['user_data_path']} -> Container:/freqtrade/user_data"
            )
            logger.info(
                f"  Config volume: Host:{user_config_json_path} -> Container:/freqtrade/config.json"
            )

            # Check if a container with the same name already exists
            try:
                existing_container = self.client.containers.get(container_name)
                if existing_container:
                    logger.warning(
                        f"Container {container_name} already exists. Stopping and removing it."
                    )
                    existing_container.stop()
                    existing_container.remove()
            except docker.errors.NotFound:
                pass  # Container doesn't exist, which is good

            container = self.client.containers.run(
                image_name,
                command=command,
                name=container_name,
                volumes=volumes,
                ports=ports,
                detach=True,
            )
            logger.info(
                f"Container {container.name} started successfully with ID {container.id}."
            )
            return {
                "id": container.id,
                "name": container.name,
                "status": container.status,
                "port": internal_bot_details["port"],
                "bot_id": internal_bot_details["bot_id"],
            }
        except docker.errors.ImageNotFound:
            logger.error(f"Docker image {image_name} not found. Please pull it first.")
            return {"error": f"Image {image_name} not found."}
        except docker.errors.APIError as e:
            logger.error(
                f"Failed to start Freqtrade container for tenant {tenant_id}: {e}"
            )
            return {"error": f"Docker API error: {e}"}
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while starting bot for tenant {tenant_id}: {e}"
            )
            return {"error": f"An unexpected error occurred: {e}"}

    def create_tenant_config_file(
        self,
        tenant_id: str,
        bot_config_data: dict,
        base_path_str: str = "docker-configs/freqtrade/configs",
    ) -> str:
        """
        Generates a Freqtrade config.json file for a given tenant.
        bot_config_data is expected to be a dictionary derived from FreqtradeConfigCreate schema.
        Returns the absolute path to the generated config.json file.
        """
        project_root = (
            Path(__file__).resolve().parents[3]
        )  # backend/app/services/orchestrator.py -> project_root
        base_path = project_root / base_path_str
        tenant_config_dir = base_path / tenant_id

        try:
            tenant_config_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {tenant_config_dir}")
        except OSError as e:
            logger.error(
                f"Error creating tenant config directory {tenant_config_dir}: {e}"
            )
            raise

        config_content = {
            "bot_name": f"ft_bot_{tenant_id}",
            "max_open_trades": bot_config_data.get("max_open_trades", 3),
            "stake_currency": bot_config_data["stake_currency"],
            "stake_amount": bot_config_data["stake_amount"],
            "dry_run": bot_config_data.get("dry_run", True),
            "exchange": {
                "name": bot_config_data["exchange_name"],
                "key": bot_config_data["api_key"],
                "secret": bot_config_data["api_secret"],
                "pair_whitelist": bot_config_data.get("pair_whitelist")
                or ["BTC/USDT", "ETH/USDT"],
                "ccxt_config": {"enableRateLimit": True},
                "ccxt_async_config": {"enableRateLimit": True},
            },
            "pairlists": [{"method": "StaticPairList"}],
            "telegram": {
                "enabled": bot_config_data.get("telegram_enabled", False),
                "token": bot_config_data.get("telegram_token", ""),
                "chat_id": bot_config_data.get("telegram_chat_id", ""),
            },
            "api_server": {
                "enabled": True,
                "listen_ip_address": "0.0.0.0",
                "listen_port": 8080,
                "username": "user",
                "password": "password",
            },
            "strategy": bot_config_data.get("strategy", "SampleStrategy"),
            "original_config_file": None,
        }

        config_file_path = tenant_config_dir / "config.json"

        try:
            with open(config_file_path, "w") as f:
                json.dump(config_content, f, indent=4)
            logger.info(f"Successfully wrote config.json to {config_file_path}")
        except IOError as e:
            logger.error(f"Error writing config.json to {config_file_path}: {e}")
            raise

        return str(config_file_path.resolve())

    def stop_bot(self, bot_id: str) -> bool:
        """
        Stops and removes the Freqtrade container with the given bot_id.
        bot_id is expected to be the container name (e.g., "freqtrade-bot-tenantX")
        """
        container_name = bot_id  # Assuming bot_id is the container name
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            container.remove()
            logger.info(f"Container {container_name} stopped and removed successfully.")
            return True
        except docker.errors.NotFound:
            logger.warning(f"Container {container_name} not found. Cannot stop.")
            return False
        except docker.errors.APIError as e:
            logger.error(f"Failed to stop/remove container {container_name}: {e}")
            return False

    def get_bot_status(self, bot_id: str) -> dict:
        """
        Gets the status of the Freqtrade container.
        bot_id is expected to be the container name (e.g., "freqtrade-bot-tenantX")
        """
        container_name = bot_id  # Assuming bot_id is the container name
        try:
            container = self.client.containers.get(container_name)
            return {
                "id": container.id,
                "name": container.name,
                "status": container.status,
                "image": container.attrs["Config"]["Image"],
                "ports": container.attrs["NetworkSettings"]["Ports"],
            }
        except docker.errors.NotFound:
            logger.warning(f"Container {container_name} not found.")
            return {"error": "Container not found", "bot_id": bot_id}
        except docker.errors.APIError as e:
            logger.error(f"Failed to get status for container {container_name}: {e}")
            return {"error": f"Docker API error: {e}", "bot_id": bot_id}

    def get_bot_logs(self, bot_id: str, tail: int = 100) -> Optional[str]:
        """
        Retrieves the logs of a specific Freqtrade container.
        bot_id is expected to be the container name.
        tail specifies the number of lines from the end of the logs to retrieve.
        """
        container_name = bot_id  # Assuming bot_id is the container name
        try:
            container = self.client.containers.get(container_name)
            logs = container.logs(tail=tail, stdout=True, stderr=True).decode("utf-8")
            logger.info(f"Retrieved logs for container {container_name}.")
            return logs
        except docker.errors.NotFound:
            logger.warning(
                f"Container {container_name} not found. Cannot retrieve logs."
            )
            return None
        except docker.errors.APIError as e:
            logger.error(f"Failed to retrieve logs for container {container_name}: {e}")
            return None
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while retrieving logs for {container_name}: {e}"
            )
            return None


if __name__ == "__main__":
    # Example Usage (for testing purposes, run from the backend directory)
    # Ensure Docker is running and freqtradeorg/freqtrade:stable image is pulled.

    orchestrator = FreqtradeOrchestrator()
    tenant_id = "tenant1_example"

    sample_bot_config_data = {
        "exchange_name": "binance",
        "api_key": "YOUR_DUMMY_API_KEY",
        "api_secret": "YOUR_DUMMY_API_SECRET",
        "dry_run": True,
        "stake_currency": "USDT",
        "stake_amount": 100.0,
        "strategy": "SampleStrategy",
        "pair_whitelist": ["BTC/USDT", "ETH/USDT", "ADA/USDT"],
        "telegram_enabled": False,
        "max_open_trades": 5,
    }

    print(f"Attempting to start bot for tenant: {tenant_id} with custom config data.")

    start_info = orchestrator.start_bot(
        tenant_id=tenant_id, bot_config_data=sample_bot_config_data
    )
    print("\nStart Info:", start_info)

    if "error" not in start_info and start_info.get("id"):
        running_bot_id = start_info["name"]
        print(f"\nBot {running_bot_id} started. Getting status...")
        status_info = orchestrator.get_bot_status(running_bot_id)
        print("Status Info:", status_info)

        print(f"\nStopping bot: {running_bot_id}")
        stop_success = orchestrator.stop_bot(running_bot_id)
        print("Stop Success:", stop_success)

        print(f"\nGetting status for bot {running_bot_id} after stopping:")
        status_info_after_stop = orchestrator.get_bot_status(running_bot_id)
        print("Status Info After Stop:", status_info_after_stop)

        project_root = Path(__file__).resolve().parents[3]
        generated_config_path = (
            project_root
            / "docker-configs"
            / "freqtrade"
            / "configs"
            / tenant_id
            / "config.json"
        )
        user_data_volume_path = (
            project_root / "docker-configs" / "freqtrade" / "user_data" / tenant_id
        )
        print(f"\nNote: Config file was generated at: {generated_config_path}")
        print(f"User data directory is at: {user_data_volume_path}")

    else:
        print(f"Could not start bot. Error: {start_info.get('error', 'Unknown error')}")

    print(
        "\nPlease ensure the Freqtrade image (freqtradeorg/freqtrade:stable) is available locally for this example to run."
    )
