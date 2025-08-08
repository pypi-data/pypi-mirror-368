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

"""Provides authentication for the user with a password or refresh token.

This module interacts with the HPS authentication service.
"""

import logging
import urllib.parse

import requests

from .exceptions import raise_for_status

log = logging.getLogger(__name__)


def authenticate(
    url: str = "https://localhost:8443/hps",
    realm: str = "rep",
    grant_type: str = "password",
    scope="openid",
    client_id: str = "rep-cli",
    client_secret: str = None,
    username: str = None,
    password: str = None,
    refresh_token: str = None,
    timeout: float = 10.0,
    verify: bool | str = True,
    **kwargs,
):
    """Authenticate the user with a password or refresh token against the HPS authentication service.

    If this method is successful, the response includes access and refresh tokens.

    Parameters
    ----------

    url : str, default: 'https://localhost:8443/hps'
        Base path for the server to call.
    realm : str, default: 'rep'
        Name of the Keycloak realm.
    grant_type: str, default: 'password'
        Authentication method.
    scope : str, default: 'openid'
        String containing one or more requested scopes.
    client_id : str, default: 'rep-cli'
        Client type.
    client_secret : str, default: None
        Client secret.
    username : str
        Username.
    password : str
        Password.
    refresh_token : str
        Refresh token.
    timeout : float, default: 10.0
        Timeout in seconds.
    verify: Union[bool, str]
        If a Boolean, whether to verify the server's TLS certificate. If a string, the
        path to the CA bundle to use. For more information, see the :class:`requests.Session`
        documentation.
    """
    auth_postfix = f"auth/realms/{realm}"
    if url.endswith(f"/{auth_postfix}") or url.endswith(f"/{auth_postfix}/"):
        auth_url = url
    else:
        auth_url = urllib.parse.urljoin(url + "/", auth_postfix)
    log.debug(f"Authenticating using {auth_url}")

    session = requests.Session()
    session.verify = verify
    session.headers = ({"content-type": "application/x-www-form-urlencoded"},)

    token_url = f"{auth_url}/protocol/openid-connect/token"

    data = {
        "client_id": client_id,
        "grant_type": grant_type,
        "scope": scope,
    }
    if client_secret is not None:
        data["client_secret"] = client_secret
    if username is not None:
        data["username"] = username
    if password is not None:
        data["password"] = password
    if refresh_token is not None:
        data["refresh_token"] = refresh_token

    data.update(**kwargs)

    log.debug(f"Retrieving access token for client {client_id} from {auth_url} using {grant_type} grant.")
    r = session.post(token_url, data=data, timeout=timeout)

    raise_for_status(r)
    return r.json()
