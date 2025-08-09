# Copyright 2025 West University of Timisoara
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import datetime
import json
import logging
import os
import re
import threading
import xml.etree.ElementTree as ET
import time
from urllib.parse import urlencode

import requests
import s3fs
from authlib.integrations.requests_client import OAuth2Session
from dateutil import parser as date_parser

from eocube.common import ROCS_DISCOVERY_URL
from eocube.common.exceptions import EOCubeAuthenticationException

log = logging.getLogger(__name__)

from eocube.integrations.auth import ROCS_DEFAULT_STORAGE_ENDPOINT
from eocube.integrations.auth.client import (
    do_requests_post,
    fetch_token_with_backoff,
    do_requests_get,
)


def get_service_client_token():
    client_id = os.environ.get("EOCUBE_CLIENT_ID", None)
    client_secret = os.environ.get("EOCUBE_CLIENT_SECRET", None)
    client_scope = os.environ.get("EOCUBE_CLIENT_SCOPE", None)
    if client_id is None or client_secret is None:
        raise Exception("EOCUBE_CLIENT_ID and EOCUBE_CLIENT_SECRET must be set")

    kws = {"client_id": client_id, "client_secret": client_secret}
    if client_scope is not None:
        scope = re.split(r"\s+", client_scope)
        kws["scope"] = scope

    return AuthClient(**kws)


def get_token_from_refresh_token(refresh_token, client_id, client_secret=None):
    # ToDo: Tracked in !10 see also #7
    if not refresh_token:
        raise EOCubeAuthenticationException("No refresh token found")

    metadata = requests.get(ROCS_DISCOVERY_URL).json()
    token_url = metadata["token_endpoint"]

    session = OAuth2Session(
        client_id=client_id, client_secret=client_secret  # None == public client
    )

    token = session.refresh_token(token_url, refresh_token=refresh_token)
    return token


def discover_client_token():
    client_id = os.environ.get(
        "EOCUBE_CLIENT_ID", None
    )  # Expected for services and notebook
    client_secret = os.environ.get(
        "EOCUBE_CLIENT_SECRET", None
    )  # Expected for services
    rocs_aai_access_token = os.environ.get("ROCS_AAI_ACCESS_TOKEN", None)
    rocs_aai_refresh_token = os.environ.get("ROCS_AAI_REFRESH_TOKEN", None)
    inside_eocube_notebook = (
        os.environ.get("INSIDE_EOCUBE_NOTEBOOK", "true").lower() == "true"
    )
    if client_id is not None and client_secret is not None:
        log.info(f"Using OIDC Client based configuration. Client: {client_id}")
        return get_service_client_token()
    elif inside_eocube_notebook:  # ToDo: At some time it should be solved by #7
        raise EOCubeAuthenticationException(
            f"Authentication using notebook runtime is not supported yet\n\n"
            "Consider using EOCube CLI based configuration: `eocube auth login`\n"
        )
        if (
            rocs_aai_access_token is None
            or rocs_aai_refresh_token is None
            or client_id is None
        ):
            raise EOCubeAuthenticationException(
                "Misconfiguration in notebook runtime setup"
            )
        credentials = get_token_from_refresh_token(
            rocs_aai_refresh_token, client_id=client_id
        )
        return credentials
    else:
        raise EOCubeAuthenticationException(
            "No supported method for retrieving credentials available"
        )


def decode_token(token):
    try:
        payload_part = token.split(".")[1]
        padded = payload_part + "=" * (-len(payload_part) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode()))
        return payload
    except Exception as e:
        log.error("Error decoding token:", e)
        raise EOCubeAuthenticationException("Error decoding token: " + str(e), e)


def _is_token_valid(token):
    try:
        payload = decode_token(token)
        exp = payload.get("exp")
        return exp and time.time() < exp - 30
    except Exception as e:
        log.error(
            f"Error validating token: {e}",
        )
        return False


class StorageCredentials(object):
    def __init__(
        self,
        endpoint,
        access_key,
        secret_key,
        session_token,
        expiration: datetime.datetime,
        leeway=300,
    ):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.session_token = session_token
        self.expiration: datetime.datetime = expiration
        self.leeway = leeway

    def is_expired(self):
        """
        Checks whether the current token is expired based on the expiration time
        and a specified leeway.

        This method calculates the difference in seconds between the expiration time
        and the current time, adjusted for the UTC timezone. If the difference is less
        than the permissible leeway, the instance is considered expired.

        :return: Returns True if the instance is expired, otherwise False.
        :rtype: bool
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        expiration = self.expiration
        diff = expiration.timestamp() - now.timestamp()
        if diff < self.leeway:
            return True
        else:
            return False


class AuthClient(object):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scope: list = ["openid", "email", "profile", "eocube-object-storage"],
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.metadata = do_requests_get(ROCS_DISCOVERY_URL).json()
        self.token_endpoint = self.metadata["token_endpoint"]
        self._token_lock = threading.Lock()
        self._storage_tokens = {}
        self._storage_tokens_lock = threading.Lock()

        self.client = OAuth2Session(
            client_id=client_id, client_secret=client_secret, scope=scope
        )

        self._token = None

    @property
    def token(self):
        if self._token is None or self._token.is_expired():
            with self._token_lock:
                self._token = fetch_token_with_backoff(
                    self.client,
                    url=self.token_endpoint,
                    grant_type="client_credentials",
                )
        return self._token

    def _credentials_are_valid(self, endpoint):
        if (
            endpoint not in self._storage_tokens
            or self._storage_tokens[endpoint].is_expired()
        ):
            return False
        else:
            return True

    def get_storage_fs(self, credentials: StorageCredentials = None):
        """Returns a fsspec filesystem for the configured credentials"""
        if credentials is None:
            credentials = self.get_storage_credentials()
        fs = s3fs.S3FileSystem(
            key=credentials.access_key,
            secret=credentials.secret_key,
            token=credentials.session_token,
            endpoint_url=credentials.endpoint,
        )
        return fs

    def get_storage_credentials(
        self, endpoint: str = None, duration_seconds: int = 3600, policy: str = None
    ):
        """
        Retrieves temporary storage credentials for a given endpoint. The credentials
        allow access to the specified storage service for a limited duration. This
        function enables fine-grained access control to the storage by optionally
        providing a policy that defines the access permissions.

        :param endpoint: The URL of the storage endpoint for which the credentials
            will be generated. If not specified, the default endpoint will be used.
        :type endpoint: str
        :param duration_seconds: The duration for which the temporary credentials
            remain valid, in seconds. If not specified, the default duration is 3600
            seconds (1 hour).
        :type duration_seconds: int
        :param policy: URL-encoded JSON-formatted policy to use as an inline session policy.
            If not provided, the policy in the JWT token will be used.
        :type policy: str
        :return: A dictionary containing the temporary credentials, including access
            keys, secret keys, and any other relevant details required to access the
            storage service.
        :rtype: dict
        """

        if endpoint is None:
            endpoint = ROCS_DEFAULT_STORAGE_ENDPOINT
        if not self._credentials_are_valid(
            endpoint
        ):  # We don't have a valid token for this endpoint
            with self._storage_tokens_lock:
                if not self._credentials_are_valid(
                    endpoint
                ):  # Double check -- due to potential concurency
                    creds = self._get_storage_credentials_using_token(
                        endpoint=endpoint,
                        token=self.token,
                        duration_seconds=duration_seconds,
                        policy=policy,
                    )
                    self._storage_tokens[endpoint] = creds
        return self._storage_tokens[endpoint]

    def _get_storage_credentials_using_access_token(
        self,
        endpoint: str,
        token: str,
        duration_seconds: int = 3600,
        policy: str = None,
    ):
        params = {
            "Action": "AssumeRoleWithWebIdentity",
            "Version": "2011-06-15",
            "WebIdentityToken": token,
            "DurationSeconds": duration_seconds,
        }

        if policy is not None:
            params["Policy"] = policy

        response = do_requests_post(
            endpoint,
            data=urlencode(params),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        root = ET.fromstring(response.text)
        ns = {"ns": "https://sts.amazonaws.com/doc/2011-06-15/"}
        creds = root.find(".//ns:Credentials", ns)
        if creds is None:
            raise Exception("Could not parse credentials from response")

        expiration_str = creds.find("ns:Expiration", ns).text
        expiration_dt = date_parser.parse(expiration_str)

        return StorageCredentials(
            endpoint=endpoint,
            access_key=creds.find("ns:AccessKeyId", ns).text,
            secret_key=creds.find("ns:SecretAccessKey", ns).text,
            session_token=creds.find("ns:SessionToken", ns).text,
            expiration=expiration_dt,
            leeway=300,
        )

    def _get_storage_credentials_using_token(
        self,
        endpoint: str,
        token: str,
        duration_seconds: int = 3600,
        policy: str = None,
    ):
        access_token = token["access_token"]
        return self._get_storage_credentials_using_access_token(
            endpoint=endpoint,
            token=access_token,
            duration_seconds=duration_seconds,
            policy=policy,
        )
