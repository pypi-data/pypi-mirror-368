import os

import pystac_client

UVT_STAC_API = "http://stac.sage.uvt.ro/"
STAC_ENDPOINT = os.environ.get("STAC_API_ENDPOINT", UVT_STAC_API)


class Client(pystac_client.Client):
    @classmethod
    def open(cls, **kwargs):
        return super().open(STAC_ENDPOINT, **kwargs)


def CatalogSearchClient(**kwargs):
    return Client.open(**kwargs)
