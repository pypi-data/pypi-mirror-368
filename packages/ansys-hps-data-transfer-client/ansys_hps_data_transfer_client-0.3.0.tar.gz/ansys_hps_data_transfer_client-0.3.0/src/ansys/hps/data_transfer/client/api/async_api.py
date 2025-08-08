# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Provides asynchronous API functionality for interacting with the Ansys HPS data transfer client.

This module includes methods and utilities for performing
data transfer operations asynchronously, managing resources, and handling client interactions.
"""

import asyncio
import builtins
from collections.abc import Awaitable, Callable
import logging
import textwrap
import time

import backoff
import humanfriendly as hf

from ..client import AsyncClient
from ..exceptions import TimeoutError
from ..models.metadata import DataAssignment
from ..models.msg import (
    CheckPermissionsResponse,
    GetPermissionsResponse,
    OpIdResponse,
    OpsResponse,
    SetMetadataRequest,
    SrcDst,
    Status,
    StorageConfigResponse,
    StoragePath,
)
from ..models.ops import Operation, OperationState
from ..models.permissions import RoleAssignment, RoleQuery
from ..utils.jitter import get_expo_backoff
from .retry import retry

log = logging.getLogger(__name__)


class AsyncDataTransferApi:
    """Provides a wrapper for the Data Transfer Worker REST API, offering an async interface."""

    def __init__(self, client: AsyncClient):
        """Initialize the async data transfer API with the client object."""
        self.dump_mode = "json"
        self.client = client

    @retry()
    async def status(self, wait=False, sleep=5, jitter=True, timeout: float | None = 20.0):
        """Provides an async interface to get the status of the worker."""

        async def _sleep():
            log.info(f"Waiting for the worker to be ready on port {self.client.binary_config.port} ...")
            s = backoff.full_jitter(sleep) if jitter else sleep

            await asyncio.sleep(s)

        url = "/"
        start = time.time()
        while True:
            if timeout is not None and (time.time() - start) > timeout:
                raise TimeoutError("Timeout waiting for worker to be ready")

            resp = await self.client.session.get(url)
            json = resp.json()
            s = Status(**json)
            if wait and not s.ready:
                await _sleep()
                continue
            return s

    @retry()
    async def operations(self, ids: list[str]):
        """Provides an async interface to get a list of operations by their IDs."""
        return await self._operations(ids)

    async def storages(self):
        """Provides an async interface to get the list of storage configurations."""
        url = "/storage"
        resp = await self.client.session.get(url)
        json = resp.json()
        return StorageConfigResponse(**json).storage

    async def copy(self, operations: list[SrcDst]):
        """Provides an async interface to copy a list of ``SrcDst`` objects."""
        return await self._exec_async_operation_req("copy", operations)

    async def exists(self, operations: list[StoragePath]):
        """Provides an async interface to check if a list of ``StoragePath`` objects exist."""
        return await self._exec_async_operation_req("exists", operations)

    async def list(self, operations: list[StoragePath]):
        """Provides an async interface to get a list of ``StoragePath`` objects."""
        return await self._exec_async_operation_req("list", operations)

    async def mkdir(self, operations: builtins.list[StoragePath]):
        """Provides an async interface to create a list of directories in the remote backend."""
        return await self._exec_async_operation_req("mkdir", operations)

    async def move(self, operations: builtins.list[SrcDst]):
        """Provides an async interface to move a list of ``SrcDst`` objects in the remote backend."""
        return await self._exec_async_operation_req("move", operations)

    async def remove(self, operations: builtins.list[StoragePath]):
        """Provides an async interface to remove files in the remote backend."""
        return await self._exec_async_operation_req("remove", operations)

    async def rmdir(self, operations: builtins.list[StoragePath]):
        """Provides an async interface to remove directories in the remote backend."""
        return await self._exec_async_operation_req("rmdir", operations)

    @retry()
    async def _exec_async_operation_req(
        self, storage_operation: str, operations: builtins.list[StoragePath] | builtins.list[SrcDst]
    ):
        url = f"/storage:{storage_operation}"
        payload = {"operations": [operation.model_dump(mode=self.dump_mode) for operation in operations]}
        resp = await self.client.session.post(url, json=payload)
        json = resp.json()
        return OpIdResponse(**json)

    async def _operations(self, ids: builtins.list[str]):
        url = "/operations"
        resp = await self.client.session.get(url, params={"ids": ids})
        json = resp.json()
        return OpsResponse(**json).operations

    @retry()
    async def check_permissions(self, permissions: builtins.list[RoleAssignment]):
        """Provides an async interface to check permissions of a list of ``RoleAssignment`` objects."""
        url = "/permissions:check"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        resp = await self.client.session.post(url, json=payload)
        json = resp.json()
        return CheckPermissionsResponse(**json)

    @retry()
    async def get_permissions(self, permissions: builtins.list[RoleQuery]):
        """Provides an async interface to get permissions of a list of ``RoleQuery`` objects."""
        url = "/permissions:get"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        resp = await self.client.session.post(url, json=payload)
        json = resp.json()
        return GetPermissionsResponse(**json)

    @retry()
    async def remove_permissions(self, permissions: builtins.list[RoleAssignment]):
        """Provides an async interface to remove permissions of a list of ``RoleAssignment`` objects."""
        url = "/permissions:remove"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        await self.client.session.post(url, json=payload)

    @retry()
    async def set_permissions(self, permissions: builtins.list[RoleAssignment]):
        """Provides an async interface to set permissions of a list of ``RoleAssignment`` objects."""
        url = "/permissions:set"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        await self.client.session.post(url, json=payload)

    @retry()
    async def get_metadata(self, paths: builtins.list[str | StoragePath]):
        """Provides an async interface to get metadata of a list of ``StoragePath`` objects."""
        url = "/metadata:get"
        paths = [p if isinstance(p, str) else p.path for p in paths]
        payload = {"paths": paths}
        resp = await self.client.session.post(url, json=payload)
        json = resp.json()
        return OpIdResponse(**json)

    @retry()
    async def set_metadata(self, asgs: dict[str | StoragePath, DataAssignment]):
        """Provides an async interface to set metadata of a list of ``DataAssignment`` objects."""
        url = "/metadata:set"
        d = {k if isinstance(k, str) else k.path: v for k, v in asgs.items()}
        req = SetMetadataRequest(metadata=d)
        resp = await self.client.session.post(url, json=req.model_dump(mode=self.dump_mode))
        json = resp.json()
        return OpIdResponse(**json)

    async def wait_for(
        self,
        operation_ids: builtins.list[str | Operation],
        timeout: float | None = None,
        interval: float = 0.1,
        cap: float = 2.0,
        raise_on_error: bool = False,
        progress_handler: Callable[[str, float], Awaitable[None]] = None,
    ):
        """Provides an async interface to wait for a list of operations to complete.

        Parameters
        ----------
        operation_ids: list[str | Operation]
            The list of operation ids to wait for.
        timeout: float | None
            The maximum time to wait for the operations to complete.
        interval: float
            The interval between checks for the operations to complete.
        cap: float
            The maximum backoff value used to calculate the next wait time. Default is 2.0.
        raise_on_error: bool
            Raise an exception if an error occurs. Default is False.
        progress_handler: Callable[[str, float], None]
            A async function to handle progress updates. Default is None.

        """
        if not isinstance(operation_ids, list):
            operation_ids = [operation_ids]
        operation_ids = [op.id if isinstance(op, Operation | OpIdResponse) else op for op in operation_ids]
        start = time.time()
        attempt = 0
        op_str = textwrap.wrap(", ".join(operation_ids), width=60, placeholder="...")
        # log.debug(f"Waiting for operations to complete: {op_str}")
        while True:
            attempt += 1
            try:
                ops = await self._operations(operation_ids)
                so_far = hf.format_timespan(time.time() - start)
                log.debug(f"Waiting for {len(operation_ids)} operations to complete, {so_far} so far")
                if self.client.binary_config.debug:
                    for op in ops:
                        fields = [
                            f"id={op.id}",
                            f"state={op.state}",
                            f"start={op.started_at}",
                            f"succeeded_on={op.succeeded_on}",
                        ]
                        if op.progress > 0:
                            fields.append(f"progress={op.progress:.3f}")
                        log.debug(f"- Operation '{op.description}' {' '.join(fields)}")
                if progress_handler is not None:
                    for op in ops:
                        await progress_handler(op.id, op.progress)
                if all(op.state in [OperationState.Succeeded, OperationState.Failed] for op in ops):
                    break
            except Exception as e:
                log.debug(f"Error getting operations: {e}")
                if raise_on_error:
                    raise

            if timeout is not None and (time.time() - start) > timeout:
                raise TimeoutError("Timeout waiting for operations to complete")

            # TODO: Adjust based on transfer speed and file size
            duration = get_expo_backoff(interval, attempts=attempt, cap=cap, jitter=True)
            if self.client.binary_config.debug:
                log.debug(f"Next check in {hf.format_timespan(duration)} ...")
            await asyncio.sleep(duration)

        duration = hf.format_timespan(time.time() - start)
        log.debug(f"Operations completed after {duration}: {op_str}")
        return ops
