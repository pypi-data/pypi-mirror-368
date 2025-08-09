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
import contextlib
import json
import logging
import os
import threading
import time
import webbrowser
from datetime import datetime
from urllib.parse import urlencode

import click
import keyring
import requests
from authlib.integrations.requests_client import OAuth2Session

from eocube.cli import console
import xml.etree.ElementTree as ET
from dateutil import parser as date_parser

from eocube.common import ROCS_DISCOVERY_URL
from eocube.common.auth import (
    discover_client_token,
    StorageCredentials,
    _is_token_valid,
)
from eocube.common.exceptions import EOCubeAuthenticationException

log = logging.getLogger("rich")

EOCUBE_CLI_CLIENT_ID = "eocube-cli"
EOCUBE_CLI_REDIRECT_URI = "http://localhost:5123/callback"

login_done = threading.Event()

authorize_url = None
token_url = None


def get_token():
    access_token = keyring.get_password("eocube-cli", "access-token")
    refresh_token = keyring.get_password("eocube-cli", "offline-refresh-token")

    if access_token and _is_token_valid(access_token):
        log.info("✅ Found valid access token in keyring")
        return access_token
    else:
        log.warning("No token found")

    if not refresh_token:
        raise click.ClickException(
            "❌ No refresh token. Please login: `eocube auth login`"
        )

    # Facem refresh cu authlib
    metadata = requests.get(ROCS_DISCOVERY_URL).json()
    token_url = metadata["token_endpoint"]

    log.warning("🔄 Token expired or missing. Trying to refresh ...")

    session = OAuth2Session(
        client_id=EOCUBE_CLI_CLIENT_ID, client_secret=None  # public client
    )

    token = session.refresh_token(token_url, refresh_token=refresh_token)

    new_access_token = token["access_token"]
    new_refresh_token = token.get("refresh_token", refresh_token)

    keyring.set_password("eocube-cli", "access-token", new_access_token)
    keyring.set_password("eocube-cli", "offline-refresh-token", new_refresh_token)

    log.info("✅ Saved new tokens in keyring.")

    return new_access_token


@click.group("auth")
def auth_cli():
    """Authentication related functionality"""


@auth_cli.command("info")
def info_authentication():
    """Afișează informații despre utilizatorul autentificat"""

    token = get_token()
    try:
        payload_part = token.split(".")[1]
        padded = payload_part + "=" * (-len(payload_part) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(padded.encode()))

        console.print("🧾 Token Information:\n")

        for key in [
            "sub",
            "preferred_username",
            "email",
            "name",
            "given_name",
            "family_name",
            "roles",
            "scope",
            "policy",
        ]:
            if key in decoded:
                console.print(f"{key:>20}: {decoded[key]}")
        if "exp" in decoded:
            exp_time = datetime.fromtimestamp(decoded["exp"])
            console.print(f"{'exp':>20}: {decoded['exp']} (expires on {exp_time})")

        # 🔐 Roluri, dacă există
        if "realm_access" in decoded and "roles" in decoded["realm_access"]:
            roles = decoded["realm_access"]["roles"]
            console.print(f"{'roles':>20}: {', '.join(roles)}")
    except Exception as e:
        console.print("⚠️ Could not decode payload", e)


def login_with_device_flow():

    metadata = requests.get(ROCS_DISCOVERY_URL).json()
    device_auth_url = metadata["device_authorization_endpoint"]
    token_url = metadata["token_endpoint"]
    device_resp = requests.post(
        device_auth_url,
        data={
            "client_id": EOCUBE_CLI_CLIENT_ID,
            "scope": "openid offline_access eocube-object-storage",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()

    session = OAuth2Session(EOCUBE_CLI_CLIENT_ID)

    print("\n=== Authentication required ===")
    print("🔗 Open browser and visit:")
    print(device_resp["verification_uri_complete"])
    print("📋 Enter code if requested:", device_resp["user_code"])

    while True:
        time.sleep(device_resp.get("interval", 5))
        token_resp = requests.post(
            token_url,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_resp["device_code"],
                "client_id": EOCUBE_CLI_CLIENT_ID,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_resp.status_code == 200:
            oauth_token = token_resp.json()
            print("✅ Authentication to EOCube.ro successful!")
            keyring.set_password(
                "eocube-cli", "offline-refresh-token", oauth_token["refresh_token"]
            )
            keyring.set_password(
                "eocube-cli", "access-token", oauth_token["access_token"]
            )
            break
        else:
            err = token_resp.json().get("error")
            if err in ["authorization_pending", "slow_down"]:
                print(f"Waiting for authorization... ({err})")
                continue
            else:
                raise EOCubeAuthenticationException(
                    f"Failed to authenticate using device flow: {err}"
                )


@auth_cli.command("login")
@click.option("--device-flow", is_flag=True, help="Use OIDC device flow", default=False)
def login(device_flow=False):
    if "EOCUBE_CLIENT_ID" in os.environ:  # Using env driven login
        return login_with_client_credentials()
    elif device_flow:
        return login_with_device_flow()
    else:
        return login_using_browser()


def login_with_client_credentials():
    auth_client = discover_client_token()
    oauth_token = auth_client.token
    if "refresh_token" in oauth_token:  # This should never be true
        keyring.set_password(
            "eocube-cli", "offline-refresh-token", oauth_token["refresh_token"]
        )
    keyring.set_password("eocube-cli", "access-token", oauth_token["access_token"])
    console.print("🔐 Saved tokens in keyring")


def login_using_browser():
    from flask import Flask, request

    """Login to EOCube.ro"""

    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    app = Flask(__name__)
    server_thread = None

    def start_oauth_flow():
        global authorize_url
        global token_url
        oauth = OAuth2Session(
            EOCUBE_CLI_CLIENT_ID, redirect_uri=EOCUBE_CLI_REDIRECT_URI
        )
        metadata = requests.get(ROCS_DISCOVERY_URL).json()
        authorize_url = metadata["authorization_endpoint"]
        token_url = metadata["token_endpoint"]
        uri, state = oauth.create_authorization_url(
            authorize_url, scope="openid offline_access eocube-object-storage"
        )
        webbrowser.open(uri)
        return oauth

    def run_flask():
        app.run(port=5123, use_reloader=False)

    def shutdown_server():
        func = request.environ.get("werkzeug.server.shutdown")
        if func:
            func()

    @app.route("/callback")
    def callback():
        global oauth_token
        global token_url

        code = request.args.get("code")
        if not code:
            return "❌ No code received. Something went wrong."

        token = app.oauth_session.fetch_token(token_url, code=code)

        oauth_token = token  # salvează tokenul pt codul principal
        login_done.set()
        shutdown_server()  # oprește Flask

        return """
        ✅ Te-ai autentificat!<br><br>
        Poți închide fereastra.<br>
        Vezi terminalul pentru token-uri.
        """

    console.print("🚀 Starting login...")
    # global server_thread
    server_thread = threading.Thread(target=run_flask)
    server_thread.start()
    time.sleep(1)
    app.oauth_session = start_oauth_flow()
    login_done.wait()

    keyring.set_password(
        "eocube-cli", "offline-refresh-token", oauth_token["refresh_token"]
    )
    keyring.set_password("eocube-cli", "access-token", oauth_token["access_token"])
    console.print("🔐 Saved tokens in keyring")
    os._exit(0)


def get_storage_credentials_using_access_token(
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

    response = requests.post(
        endpoint,
        data=urlencode(params),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    root = ET.fromstring(response.text)
    ns = {"ns": "https://sts.amazonaws.com/doc/2011-06-15/"}
    creds = root.find(".//ns:Credentials", ns)
    if creds is None:
        message = root.find(".//ns:Message", ns).text
        raise Exception(f"Could not get credentials from response: {message}")

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


@auth_cli.command("get-storage-credentials-with-token")
@click.option(
    "--endpoint",
    prompt=False,
    help="Storage endpoint",
    default="https://storage.svc.uvt-01.eocube.ro/",
)
@click.option("--token", prompt=True, help="OIDC access token")
@click.option(
    "--duration-seconds", prompt=False, help="Duration in seconds", default=3600
)
def get_storage_credentials_with_token(endpoint, token, duration_seconds=3600):
    creds = get_storage_credentials_using_access_token(
        endpoint, token, duration_seconds=duration_seconds
    )
    console.print(f"Access Key {creds.access_key}")
    console.print(f"Secret Key {creds.secret_key}")
    console.print(f"Session Token {creds.session_token}")
    console.print(f"Expiration {creds.expiration}")


@auth_cli.command("logout")
def logout():
    """Logout from EOCloud.Ro"""

    refresh_token = keyring.get_password("eocube-cli", "offline-refresh-token")
    access_token = keyring.get_password("eocube-cli", "access-token")

    metadata = requests.get(ROCS_DISCOVERY_URL).json()
    revocation_endpoint = metadata.get("revocation_endpoint")
    if not revocation_endpoint:
        console.print("❌ IdP does not provide `revocation_endpoint` in metadata.")
        return

    client_id = EOCUBE_CLI_CLIENT_ID
    client_secret = None  # dacă e public client

    def revoke(token, token_type_hint):
        data = {
            "client_id": client_id,
            "token": token,
            "token_type_hint": token_type_hint,
        }
        if client_secret:
            data["client_secret"] = client_secret

        resp = requests.post(revocation_endpoint, data=data)
        if resp.status_code == 200:
            console.print(f"🔒 Token ({token_type_hint}) was revoked.")
        else:
            console.print(
                f"⚠️ Error revoking({token_type_hint}): {resp.status_code} {resp.text}"
            )

    if refresh_token:
        revoke(refresh_token, "refresh_token")
        keyring.delete_password("eocube-cli", "offline-refresh-token")
        console.print("🗑️ Refresh token was deleted.")

    if access_token:
        revoke(access_token, "access_token")
        keyring.delete_password("eocube-cli", "access-token")
        console.print("🗑️ Access token was deleted.")

    if not access_token and not refresh_token:
        console.print("ℹ️ No tokens in keyring.")

    console.print("✅ Logout complete.")


@auth_cli.command("get-storage-credentials")
@click.option(
    "--endpoint",
    help="Storage endpoint",
    default="https://storage.svc.uvt-01.eocube.ro/",
)
@click.option("--as-json", is_flag=True, help="Return JSON instead of plain text")
@click.option("--duration", type=int, help="Duration in seconds", default=3600)
def get_storage_credentials(endpoint, as_json=False, duration=3600):
    """Return S3 Credentials"""
    access_token = get_token()
    creds = get_storage_credentials_using_access_token(
        endpoint=endpoint, token=access_token, duration_seconds=duration
    )
    if as_json:
        print(
            json.dumps(
                {
                    "access_key": creds.access_key,
                    "secret_key": creds.secret_key,
                    "session_token": creds.session_token,
                    "expiration": creds.expiration.isoformat(),
                }
            )
        )
    else:
        console.print(f"Access Key {creds.access_key}")
        console.print(f"Secret Key {creds.secret_key}")
        console.print(f"Session Token {creds.session_token}")
        console.print(f"Expiration {creds.expiration}")


@auth_cli.command("get-access-token", help="Get OIDC Access Token")
def get_access_token_cli():
    """Return access token"""
    print(get_token())
