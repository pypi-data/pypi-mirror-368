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

"""Provides the core API functionality for interacting with the Ansys HPS data transfer client.

This module includes methods and utilities for performing
data transfer operations, managing resources, and handling client interactions.
"""

import builtins
from collections.abc import Callable
import logging
import textwrap
import time

import backoff
import humanfriendly as hf

from ..client import Client
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


class DataTransferApi:
    """Provides the data transfer API.

    Parameters
    ----------
    client: Client
        Client object.
    """

    def __init__(self, client: Client):
        """Initializes the DataTransferApi class object."""
        self.dump_mode = "json"
        self.client = client

    @retry()
    def status(self, wait=False, sleep=5, jitter=True, timeout: float | None = 20.0):
        """Get the status of the worker binary."""

        def _sleep():
            log.info(f"Waiting for the worker to be ready on port {self.client.binary_config.port} ...")
            s = backoff.full_jitter(sleep) if jitter else sleep
            time.sleep(s)

        url = "/"
        start = time.time()
        while True:
            if timeout is not None and (time.time() - start) > timeout:
                raise TimeoutError("Timeout waiting for worker to be ready")

            resp = self.client.session.get(url)
            json = resp.json()
            s = Status(**json)
            if wait and not s.ready:
                _sleep()
                continue
            return s

    @retry()
    def operations(self, ids: list[str]):
        """Get a list of operations.

        Parameters
        ----------
        ids: List[str]
            List of IDs.
        """
        return self._operations(ids)

    def storages(self):
        """Get types of storages available on the storage backend."""
        url = "/storage"
        resp = self.client.session.get(url)
        json = resp.json()
        return StorageConfigResponse(**json).storage

    def copy(self, operations: list[SrcDst]):
        """Get the API response for copying a list of files.

        Parameters
        ----------
        operations: List[SrcDst]
        """
        return self._exec_operation_req("copy", operations)

    def exists(self, operations: list[StoragePath]):
        """Check if a path exists.

        Parameters
        ----------
        operations: List[StoragePath]
        """
        return self._exec_operation_req("exists", operations)

    def list(self, operations: list[StoragePath]):
        """List files in a path.

        Parameters
        ----------
        operations: List[StoragePath]
        """
        return self._exec_operation_req("list", operations)

    def mkdir(self, operations: builtins.list[StoragePath]):
        """Create a directory.

        Parameters
        ----------
        operations: List[StoragePath]
        """
        return self._exec_operation_req("mkdir", operations)

    def move(self, operations: builtins.list[SrcDst]):
        """Move a file on the backend storage.

        Parameters
        ----------
        operations: List[SrcDst]
        """
        return self._exec_operation_req("move", operations)

    def remove(self, operations: builtins.list[StoragePath]):
        """Delete a file.

        Parameters
        ----------
        operations: List[StoragePath]
        """
        return self._exec_operation_req("remove", operations)

    def rmdir(self, operations: builtins.list[StoragePath]):
        """Delete a directory.

        Parameters
        ----------
        operations: List[StoragePath]
        """
        return self._exec_operation_req("rmdir", operations)

    @retry()
    def _exec_operation_req(
        self, storage_operation: str, operations: builtins.list[StoragePath] | builtins.list[SrcDst]
    ):
        url = f"/storage:{storage_operation}"
        payload = {"operations": [operation.model_dump(mode=self.dump_mode) for operation in operations]}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        r = OpIdResponse(**json)
        return r

    def _operations(self, ids: builtins.list[str]):
        url = "/operations"
        resp = self.client.session.get(url, params={"ids": ids})
        json = resp.json()
        return OpsResponse(**json).operations

    @retry()
    def check_permissions(self, permissions: builtins.list[RoleAssignment]):
        """Check permissions of a path (including parent directory) using a list of ``RoleAssignment`` objects.

        Parameters
        ----------
        permissions: List[RoleAssignment]
        """
        url = "/permissions:check"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return CheckPermissionsResponse(**json)

    @retry()
    def get_permissions(self, permissions: builtins.list[RoleQuery]):
        """Get permissions of a file from a list of ``RoleQuery`` objects.

        Parameters
        ----------
        permissions: List[RoleQuery]
        """
        url = "/permissions:get"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return GetPermissionsResponse(**json)

    @retry()
    def remove_permissions(self, permissions: builtins.list[RoleAssignment]):
        """Remove permissions using a list of ``RoleAssignment`` objects.

        Parameters
        ----------
        permissions: List[RoleAssignment]
        """
        url = "/permissions:remove"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        self.client.session.post(url, json=payload)

    @retry()
    def set_permissions(self, permissions: builtins.list[RoleAssignment]):
        """Set permissions using a list of ``RoleAssignment`` objects.

        Parameters
        ----------
        permissions: List[RoleAssignment]
        """
        url = "/permissions:set"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        self.client.session.post(url, json=payload)

    @retry()
    def get_metadata(self, paths: builtins.list[str | StoragePath]):
        """Get metadata of a path on the backend storage.

        Parameters
        ----------
        paths: List[str | StoragePath]
        """
        url = "/metadata:get"
        paths = [p if isinstance(p, str) else p.path for p in paths]
        payload = {"paths": paths}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return OpIdResponse(**json)

    @retry()
    def set_metadata(self, asgs: dict[str | StoragePath, DataAssignment]):
        """Set metadata for a path on the backend storage.

        Parameters
        ----------
        asgs: Dict[str | StoragePath, DataAssignment]
            List of paths with key of type string or ``StoragePath`` and value of ``DataAssignment``.
        """
        url = "/metadata:set"
        d = {k if isinstance(k, str) else k.path: v for k, v in asgs.items()}
        req = SetMetadataRequest(metadata=d)
        resp = self.client.session.post(url, json=req.model_dump(mode=self.dump_mode))
        json = resp.json()
        return OpIdResponse(**json)

    def wait_for(
        self,
        operation_ids: builtins.list[str | Operation | OpIdResponse],
        timeout: float | None = None,
        interval: float = 0.1,
        cap: float = 2.0,
        raise_on_error: bool = False,
        progress_handler: Callable[[str, float], None] = None,
    ):
        """Wait for operations to complete.

        Parameters
        ----------
        operation_ids: List[str | Operation | OpIdResponse]
            List of operation ids.
        timeout: float | None
            Timeout in seconds. Default is None.
        interval: float
            Interval in seconds. Default is 0.1.
        cap: float
            The maximum backoff value used to calculate the next wait time. Default is 2.0.
        raise_on_error: bool
            Raise an exception if an error occurs. Default is False.
        progress_handler: Callable[[str, float], None]
            A function to handle progress updates. Default is None.
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
                ops = self._operations(operation_ids)
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
                        progress_handler(op.id, op.progress)
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
            time.sleep(duration)

        duration = hf.format_timespan(time.time() - start)
        log.debug(f"Operations completed after {duration}: {op_str}")
        return ops
