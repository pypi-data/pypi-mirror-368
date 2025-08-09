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

import os


def init_gdal_environment_magic():
    os.environ["GDAL_CACHEMAX"] = "16384"
    os.environ["GDAL_DISABLE_READDIR_ON_OPEN"] = "YES"
    os.environ["CPL_VSIL_CURL_ALLOWED_EXTENSIONS"] = ".tif"
    os.environ["VSI_CACHE"] = "TRUE"
    os.environ["VSI_CACHE_SIZE"] = "100000000"


def init_notebook():
    init_gdal_environment_magic()


def init_cluster(num_workers: int = 5):
    from dask_gateway import GatewayCluster
    from dask_gateway import Gateway

    gw = Gateway()
    clusters = gw.list_clusters()
    if not clusters:
        gateway = GatewayCluster()
    elif len(clusters) > 1:
        raise Exception("To many clusters")
    else:
        gateway = clusters[0]
        gateway = gw.connect(clusters[0].name)
    gateway.scale(num_workers)  # Ask for 15 node cluster

    return gateway, gateway.get_client()
