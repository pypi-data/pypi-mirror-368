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

import asyncio
from urllib.parse import urlparse

import backoff
import requests
from authlib.integrations.requests_client import OAuth2Session

MAX_RETRY_TIME = 200


def is_transient_error(e):
    if isinstance(e, requests.exceptions.HTTPError):
        status = e.response.status_code
        return status == 429 or (500 <= status < 600)
    return True  # Dacă e un alt `RequestException`, probabil e de retry


@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.RequestException, requests.exceptions.HTTPError),
    max_time=MAX_RETRY_TIME,
    jitter="full",
    giveup=lambda e: not is_transient_error(e),
)
def fetch_token_with_backoff(
    client: OAuth2Session, url: str, grant_type="client_credentials"
):
    return client.fetch_token(url=url, grant_type=grant_type)


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_time=MAX_RETRY_TIME,
    jitter="full",
)
def do_requests_get(*args, **kwargs):
    return requests.get(*args, **kwargs)


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_time=MAX_RETRY_TIME,
    jitter="full",
)
def do_requests_post(*args, **kwargs):
    return requests.post(*args, **kwargs)


# def discover_client_token():
#     client_id = os.environ.get("EOCUBE_CLIENT_ID", None)
#     client_secret = os.environ.get("EOCUBE_CLIENT_SECRET", None)
#     client_scope = os.environ.get("EOCUBE_CLIENT_SCOPE", None)
#     if client_id is None or client_secret is None:
#         raise Exception("EOCUBE_CLIENT_ID and EOCUBE_CLIENT_SECRET must be set")
#
#     kws = {"client_id": client_id, "client_secret": client_secret}
#     if client_scope is not None:
#         scope = re.split(r"\s+", client_scope)
#         kws["scope"] = scope
#
#     return AuthClient(**kws)


def get_presigned_url(fs, bucket, key, validity=3600):
    async def _gen_url():
        return await fs.s3.generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=validity
        )

    return asyncio.run(_gen_url())


def get_eocube_sign(fs, validity=60 * 60 * 24 * 7):
    def _sign(obj):
        if isinstance(obj, dict):
            features = obj.get("features", [])
            for feature in features:
                assets = feature.get("assets")
                for asset_name, asset_spec in assets.items():
                    asset_href = asset_spec.get("href")
                    if not asset_href:
                        continue
                    url_spec = urlparse(asset_href)
                    if url_spec.scheme != "s3":
                        continue
                    bucket_name = url_spec.netloc
                    path = url_spec.path
                    new_url = get_presigned_url(fs, bucket_name, path, validity)
                    asset_spec["href"] = new_url

    return _sign
