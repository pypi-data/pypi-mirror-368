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

import requests
from authlib.jose import JsonWebKey, jwt
from authlib.jose.errors import InvalidClaimError

from eocube.common import ROCS_DISCOVERY_URL

jwks = None
jwks_key_set = None


def update_jwks():
    """Update JWKS certificates"""
    global jwks
    global jwks_key_set
    r = requests.get(ROCS_DISCOVERY_URL)
    r.raise_for_status()
    discovery = r.json()
    jwks_uri = discovery["jwks_uri"]
    jwks = requests.get(jwks_uri).json()
    jwks_key_set = JsonWebKey.import_key_set(jwks)


def validate_token(token, audience=None):
    global jwks_key_set
    if jwks is None or jwks_key_set is None:
        update_jwks()

    claims = jwt.decode(token, jwks_key_set)
    claims.validate()
    aud = claims.get("aud", None)
    if aud and audience and audience not in aud:
        raise InvalidClaimError(aud)
    return claims


if __name__ == "__main__":
    update_jwks()
    print(
        validate_token(
            "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI4N0F4YUw2MjVac3loWERWbG1hWVVoMWlRVjVGc2RORUlaX1N2MnVpM0Y4In0.eyJleHAiOjE3NDg3MDg3MTgsImlhdCI6MTc0ODcwODQxOCwiYXV0aF90aW1lIjoxNzQ3MjM0MTM2LCJqdGkiOiJjYTg1MmY2Yi1jMmUyLTQ3YWQtODAzZS0xOWMwZTE0OTk1NmQiLCJpc3MiOiJodHRwczovL2FhaS5lb2N1YmUucm8vcmVhbG1zL3JvY3MiLCJhdWQiOlsiYWNjb3VudCIsImVvY3ViZS1vYmplY3Qtc3RvcmFnZSJdLCJzdWIiOiJkM2JhOTAyZC0zYTUxLTRlNTUtYWVlNy1mNjgyNjJiMTNlOGMiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJlb2N1YmUtY2xpIiwic2lkIjoiYjE0NmY0ZTktMmRhNS00MTgxLWIzZDgtMTZmZDFmMTk4ZWFhIiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLXJvY3MiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19LCJlb2N1YmUtb2JqZWN0LXN0b3JhZ2UiOnsicm9sZXMiOlsiZW9jdWJlLW9iamVjdC1zdG9yYWdlIl19fSwic2NvcGUiOiJvcGVuaWQgb2ZmbGluZV9hY2Nlc3MgZW9jdWJlLW9iamVjdC1zdG9yYWdlIHByb2ZpbGUgZW1haWwiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwibmFtZSI6Ik1hcmlhbiBOZWFndWwiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJtYXJpYW4ubmVhZ3VsIiwiZ2l2ZW5fbmFtZSI6Ik1hcmlhbiIsImZhbWlseV9uYW1lIjoiTmVhZ3VsIiwiZW1haWwiOiJtYXJpYW4ubmVhZ3VsQGUtdXZ0LnJvIiwicG9saWN5IjpbImVvY3ViZS1yZWd1bGFyLXVzZXIiLCJjb25zb2xlQWRtaW4iXX0.I5ptRpmM5z9soNp9pq7cChOx0NxGmskA6AzaAOAUigNZy5i7fQR9gFyEfPH9QdKPeaDIco6wSJr7-qcg2gmy2SvtEPdtzqArfPNDK3V7Rtnhq2_PX1FDi6Uqqi-55-haoxAuLqHSAt2KiCT3s02ASNJQGrTJq5juiDn1nMojUvRcjfNi9ogc4eFNB4ZPHonuugIceUogxj-WH6IrCf3OWAtqUGn2sYg56cH56fddlkivN_zEgSJNWvzw7m-nQYzrqadQuztspJT610GBThchanhpAbEoxSHZHRIsD9qskWWgWFcDSlkuUgGeq8a3khC5FaxrA2-bULkCsq3RTXV0HA"
        )
    )
