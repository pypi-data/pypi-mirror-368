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

import random
import tempfile
import uuid

import fsspec
import numpy as np
import pystac
import rasterio
import rasterio.windows
import shapely
from fsspec.implementations.local import LocalFileSystem
from shapely import box, GeometryCollection

from eocube.raster.utils import get_raster_patches


class OutputPatchHandler:
    def __init__(
        self,
        output_file_path: str,
        item: pystac.Item,
        patch_width: int = 256,
        patch_height: int = 256,
        stride: int = 256,
        assets: list = ["B02", "B03", "B04"],
        reference_asset: str = "B02",
        aoi: GeometryCollection = None,
        filesystem: fsspec.AbstractFileSystem = None,
        dtype: np.dtype = np.float32,
        shuffle: bool = False,
    ) -> None:
        """

        :param output_file_path: Destination file inside the destination filesystem (temporary file might be created)
        :param item: Input Stac Item
        :param patch_width: width of the patch
        :param patch_height: height of the patch
        :param stride: the overlap of the patches
        :param assets: list of asset names to use for data retrieval
        :param reference_asset: what asset to use as reference for generating the patches and output file
        :param aoi: Area o interest. Only patches intersecting this area are considered. Needs to be in the same projection as the data. No check is done.
        :param filesystem: Filesystem to use for uploading the result file
        :param dtype: data type of the output product
        :param shuffle: randomize the patch order
        """
        self.output_file_path = output_file_path
        self.item = item
        self.width = patch_width
        self.height = patch_height
        self.stride = stride
        self.assets = assets
        self.profile = None
        self.uuid = uuid.uuid4()
        self._tmp_file_name = f"{self.uuid.hex}.tif"
        if aoi is None:
            self.aoi = aoi
        elif isinstance(aoi, shapely.Geometry):
            self.aoi = aoi
        elif isinstance(aoi, tuple) or isinstance(aoi, list):
            self.aoi = shapely.box(*aoi)
        else:
            raise NotImplementedError(
                "AOI needs to be a shapely Geometry, a tuple or None "
            )
        self.filesystem = filesystem
        self._rios = {}
        self._index = 0  # Used by iterator
        if filesystem is None:
            self.filesystem = LocalFileSystem()
        else:
            self.filesystem = filesystem
        if reference_asset not in self.item.assets:
            raise KeyError(
                f"Reference asset: {reference_asset} not in STAC item {item.id} assets"
            )

        with rasterio.open(self.item.assets[reference_asset].href) as rio:
            self.profile = rio.profile.copy()
            self.profile["dtype"] = dtype
            self.patches = []
            for patch in get_raster_patches(
                rio, tile_width=self.width, tile_height=self.height, stride=self.stride
            ):
                bounds = rasterio.windows.bounds(
                    patch, transform=self.profile["transform"]
                )
                bbox = box(*bounds)
                if self.aoi is not None:
                    if not self.aoi.intersects(bbox):
                        continue  # Ignore box as it does not intersect with the AOI
                self.patches.append(patch)
            if shuffle:
                random.shuffle(self.patches)

        for asset in self.assets:
            if asset not in self.item.assets:
                raise KeyError(f"Asset: {asset} not in STAC item {item.id} assets")
            self._rios[asset] = rasterio.open(self.item.assets[asset].href)
        self._named_temp_file_context = tempfile.NamedTemporaryFile(
            suffix="_rocube.tif"
        )
        print(f"Destination file {self._named_temp_file_context.name}")
        self.rio = rasterio.open(
            self._named_temp_file_context.name, "w", **self.profile
        )

    def __enter__(self):
        return self

    def flush(self):
        """Function called before actual writing in order to flush any buffers

        :return:
        """
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()
        self.rio.close()
        with open(self._named_temp_file_context.name, "rb") as source_f:
            with self.filesystem.open(self.output_file_path, "wb") as dest_f:
                dest_f.write(source_f.read())
                print(f"Saved output to: {self.output_file_path}")

        for k, v in self._rios.items():
            if isinstance(v, rasterio.DatasetReader):
                v.close()

    def __len__(self):
        return len(self.patches)

    def __getitem__(self, idx):
        # window = self.patches[idx]
        return self._get_data(idx)

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self.patches):
            window = self.patches[self._index]
            self._index += 1
            # return self._get_data(window)
            return self._get_data(self._index)
        else:
            raise StopIteration

    def _get_data(self, idx):  # window
        window = self.patches[idx]
        bounds = rasterio.windows.bounds(window, transform=self.profile["transform"])
        rez = {"_bounds": bounds}
        for asset in self.assets:
            rio = self._rios[asset]
            win = rasterio.windows.from_bounds(*bounds, transform=rio.transform)
            data = rio.read(1, window=win)
            rez[asset] = data
        return rez

    def write(self, data: np.ndarray, idx: dict):
        """Write back the result of an processing

        :param data: Numpy array of the data to be written
        :param idx: original idx of reference patch used for generating the data. Valid only in the current context
        """
        window = self.patches[idx]
        if len(data.shape) == 2:
            self.rio.write(data, 1, window=window)
        elif len(data.shape) == 3:  # We assume channel first encoding
            channels = data.shape[0]
            for ch in range(0, channels):
                chidx = ch + 1
                self.rio.write(data[ch, ...], chidx, window=window)
        else:
            raise NotImplementedError("Unsupported shape.")


if __name__ == "__main__":
    import requests
    import tqdm

    id = "S2A_MSIL1C_20210816T092031_N0301_R093_T34TFQ_20210816T102826"

    test_url = f"https://stac.sage.uvt.ro/collections/sentinel-2-l1c/items/{id}"
    item = requests.get(test_url).json()
    stac_item = pystac.Item.from_dict(item)

    count = 0
    with OutputPatchHandler(
        f"out-{id}.tif",
        stac_item,
        patch_width=256,
        patch_height=256,
        stride=200,
        dtype=np.float32,
        shuffle=True,
    ) as result:
        for patch in tqdm.tqdm(result):
            ###
            # Do Some Processing
            data = np.zeros((256, 256), np.float32)
            data = data + count
            count += 1
            # End Processing
            ###

            # Write the result
            result.write(data, patch)
