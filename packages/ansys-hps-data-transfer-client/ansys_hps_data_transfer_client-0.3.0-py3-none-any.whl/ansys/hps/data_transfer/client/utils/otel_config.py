# Copyright (C) 2025 ANSYS, Inc. and/or its affiliates.
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

"""Provides utilities for configuring OpenTelemetry (Otel) settings for the Ansys HPS data transfer client.

This module allows setting up environment variables required
for telemetry data export and resource attributes.
"""

import os


def set_otel_config(exporter_url, resource_attributes=None, headers=None, exporter_type=None):
    """Set data transfer worker Otel configuration using environment variables before starting the data transfer worker.

    ANSYS_DT_OTEL__EXPORTER_URL - Otel exporter url.
    ANSYS_DT_OTEL__RESOURCE_ATTRIBUTES - key-value pairs of resource attributes to be passed to the Otel SDK.
    ANSYS_DT_OTEL__HEADERS - key-value pairs of headers to be associated with gRPC requests.
    ANSYS_DT_OTEL__EXPORTER_TYPE - Otel exporter type.
    ANSYS_DT_OTEL__ENABLED - enables Otel.
    """
    os.environ["ANSYS_DT_OTEL__ENABLED"] = "True"
    if exporter_url is not None:
        os.environ["ANSYS_DT_OTEL__EXPORTER_URL"] = str(exporter_url)
    if exporter_type is not None:
        os.environ["ANSYS_DT_OTEL__EXPORTER_TYPE"] = exporter_type
    if resource_attributes is not None:
        os.environ["ANSYS_DT_OTEL__RESOURCE_ATTRIBUTES"] = str(resource_attributes)
    if headers is not None:
        os.environ["ANSYS_DT_OTEL__HEADERS"] = str(headers)
