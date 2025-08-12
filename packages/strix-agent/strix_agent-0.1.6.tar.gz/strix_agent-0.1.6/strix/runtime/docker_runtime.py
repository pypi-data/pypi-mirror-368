import logging
import os
import secrets
import socket
import time
from pathlib import Path
from typing import cast

import docker
from docker.errors import DockerException, NotFound
from docker.models.containers import Container

from .runtime import AbstractRuntime, SandboxInfo


STRIX_AGENT_LABEL = "StrixAgent_ID"
STRIX_SCAN_LABEL = "StrixScan_ID"
STRIX_IMAGE = os.getenv("STRIX_IMAGE", "ghcr.io/usestrix/strix-sandbox:0.1.4")
logger = logging.getLogger(__name__)

_initialized_volumes: set[str] = set()


class DockerRuntime(AbstractRuntime):
    def __init__(self) -> None:
        try:
            self.client = docker.from_env()
        except DockerException as e:
            logger.exception("Failed to connect to Docker daemon")
            raise RuntimeError("Docker is not available or not configured correctly.") from e

    def _generate_sandbox_token(self) -> str:
        return secrets.token_urlsafe(32)

    def _get_scan_id(self, agent_id: str) -> str:
        try:
            from strix.cli.tracer import get_global_tracer

            tracer = get_global_tracer()
            if tracer and tracer.scan_config:
                return str(tracer.scan_config.get("scan_id", "default-scan"))
        except ImportError:
            logger.debug("Failed to import tracer, using fallback scan ID")
        except AttributeError:
            logger.debug("Tracer missing scan_config, using fallback scan ID")

        return f"scan-{agent_id.split('-')[0]}"

    def _find_available_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return cast("int", s.getsockname()[1])

    def _get_workspace_volume_name(self, scan_id: str) -> str:
        return f"strix-workspace-{scan_id}"

    def _get_sandbox_by_agent_id(self, agent_id: str) -> Container | None:
        try:
            containers = self.client.containers.list(
                filters={"label": f"{STRIX_AGENT_LABEL}={agent_id}"}
            )
            if not containers:
                return None
            if len(containers) > 1:
                logger.warning(
                    "Multiple sandboxes found for agent ID %s, using the first one.", agent_id
                )
            return cast("Container", containers[0])
        except DockerException as e:
            logger.warning("Failed to get sandbox by agent ID %s: %s", agent_id, e)
            return None

    def _ensure_workspace_volume(self, volume_name: str) -> None:
        try:
            self.client.volumes.get(volume_name)
            logger.info(f"Using existing workspace volume: {volume_name}")
        except NotFound:
            self.client.volumes.create(name=volume_name, driver="local")
            logger.info(f"Created new workspace volume: {volume_name}")

    def _copy_local_directory_to_container(self, container: Container, local_path: str) -> None:
        import tarfile
        from io import BytesIO

        try:
            local_path_obj = Path(local_path).resolve()
            if not local_path_obj.exists() or not local_path_obj.is_dir():
                logger.warning(f"Local path does not exist or is not a directory: {local_path_obj}")
                return

            logger.info(f"Copying local directory {local_path_obj} to container {container.id}")

            tar_buffer = BytesIO()
            with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
                for item in local_path_obj.rglob("*"):
                    if item.is_file():
                        arcname = item.relative_to(local_path_obj)
                        tar.add(item, arcname=arcname)

            tar_buffer.seek(0)

            container.put_archive("/shared_workspace", tar_buffer.getvalue())

            container.exec_run(
                "chown -R pentester:pentester /shared_workspace && chmod -R 755 /shared_workspace",
                user="root",
            )

            logger.info(
                f"Successfully copied {local_path_obj} to /shared_workspace in container "
                f"{container.id}"
            )

        except (OSError, DockerException):
            logger.exception("Failed to copy local directory to container")

    async def create_sandbox(
        self, agent_id: str, existing_token: str | None = None, local_source_path: str | None = None
    ) -> SandboxInfo:
        sandbox = self._get_sandbox_by_agent_id(agent_id)
        auth_token = existing_token or self._generate_sandbox_token()

        scan_id = self._get_scan_id(agent_id)
        volume_name = self._get_workspace_volume_name(scan_id)

        self._ensure_workspace_volume(volume_name)

        if not sandbox:
            logger.info("Creating new Docker sandbox for agent %s", agent_id)
            try:
                tool_server_port = self._find_available_port()
                caido_port = self._find_available_port()

                volumes_config = {volume_name: {"bind": "/shared_workspace", "mode": "rw"}}
                container_name = f"strix-{agent_id}"

                sandbox = self.client.containers.run(
                    STRIX_IMAGE,
                    command="sleep infinity",
                    detach=True,
                    name=container_name,
                    hostname=container_name,
                    ports={
                        f"{tool_server_port}/tcp": tool_server_port,
                        f"{caido_port}/tcp": caido_port,
                    },
                    cap_add=["NET_ADMIN", "NET_RAW"],
                    labels={
                        STRIX_AGENT_LABEL: agent_id,
                        STRIX_SCAN_LABEL: scan_id,
                    },
                    environment={
                        "PYTHONUNBUFFERED": "1",
                        "STRIX_AGENT_ID": agent_id,
                        "STRIX_SANDBOX_TOKEN": auth_token,
                        "STRIX_TOOL_SERVER_PORT": str(tool_server_port),
                        "CAIDO_PORT": str(caido_port),
                    },
                    volumes=volumes_config,
                    tty=True,
                )
                logger.info(
                    "Created new sandbox %s for agent %s with shared workspace %s",
                    sandbox.id,
                    agent_id,
                    volume_name,
                )
            except DockerException as e:
                raise RuntimeError(f"Failed to create Docker sandbox: {e}") from e

        assert sandbox is not None
        if sandbox.status != "running":
            sandbox.start()
            time.sleep(15)

        if local_source_path and volume_name not in _initialized_volumes:
            self._copy_local_directory_to_container(sandbox, local_source_path)
            _initialized_volumes.add(volume_name)

        sandbox_id = sandbox.id
        if sandbox_id is None:
            raise RuntimeError("Docker container ID is unexpectedly None")

        tool_server_port_str = sandbox.attrs["Config"]["Env"][
            next(
                (
                    i
                    for i, s in enumerate(sandbox.attrs["Config"]["Env"])
                    if s.startswith("STRIX_TOOL_SERVER_PORT=")
                ),
                -1,
            )
        ].split("=")[1]
        tool_server_port = int(tool_server_port_str)

        api_url = await self.get_sandbox_url(sandbox_id, tool_server_port)

        return {
            "workspace_id": sandbox_id,
            "api_url": api_url,
            "auth_token": auth_token,
            "tool_server_port": tool_server_port,
        }

    async def get_sandbox_url(self, sandbox_id: str, port: int) -> str:
        try:
            container = self.client.containers.get(sandbox_id)
            container.reload()

            host = "localhost"
            if "DOCKER_HOST" in os.environ:
                docker_host = os.environ["DOCKER_HOST"]
                if "://" in docker_host:
                    host = docker_host.split("://")[1].split(":")[0]

        except NotFound:
            raise ValueError(f"Sandbox {sandbox_id} not found.") from None
        except DockerException as e:
            raise RuntimeError(f"Failed to get sandbox URL for {sandbox_id}: {e}") from e
        else:
            return f"http://{host}:{port}"

    async def destroy_sandbox(self, sandbox_id: str) -> None:
        logger.info("Destroying Docker sandbox %s", sandbox_id)
        try:
            container = self.client.containers.get(sandbox_id)

            scan_id = None
            if container.labels and STRIX_SCAN_LABEL in container.labels:
                scan_id = container.labels[STRIX_SCAN_LABEL]

            container.stop()
            container.remove()
            logger.info("Successfully destroyed sandbox %s", sandbox_id)

            if scan_id:
                await self._cleanup_workspace_if_empty(scan_id)

        except NotFound:
            logger.warning("Sandbox %s not found for destruction.", sandbox_id)
        except DockerException as e:
            logger.warning("Failed to destroy sandbox %s: %s", sandbox_id, e)

    async def _cleanup_workspace_if_empty(self, scan_id: str) -> None:
        try:
            volume_name = self._get_workspace_volume_name(scan_id)

            containers = self.client.containers.list(
                all=True, filters={"label": f"{STRIX_SCAN_LABEL}={scan_id}"}
            )

            if not containers:
                try:
                    volume = self.client.volumes.get(volume_name)
                    volume.remove()
                    logger.info(
                        f"Cleaned up workspace volume {volume_name} for completed scan {scan_id}"
                    )

                    _initialized_volumes.discard(volume_name)

                except NotFound:
                    logger.debug(f"Volume {volume_name} already removed")
                except DockerException as e:
                    logger.warning(f"Failed to remove volume {volume_name}: {e}")

        except DockerException as e:
            logger.warning("Error during workspace cleanup for scan %s: %s", scan_id, e)

    async def cleanup_scan_workspace(self, scan_id: str) -> None:
        await self._cleanup_workspace_if_empty(scan_id)
