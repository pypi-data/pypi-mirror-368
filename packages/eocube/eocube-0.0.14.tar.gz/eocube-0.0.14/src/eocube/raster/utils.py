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

import math

from rasterio.windows import Window
from rasterio import DatasetReader


def get_raster_patches(rio: DatasetReader, tile_width=256, tile_height=256, stride=256):
    """Generate raster patches

    :param rio: rasterio DatasetReaser
    :param tile_width: Width of the patch
    :param tile_height: Height of the patch
    :param stride: The stride of the patches (offset to use between subsequent patches)
    """
    image_height, image_width = rio.shape
    window_width, window_height = tile_width, tile_height
    if tile_width != stride:
        xtiles = math.ceil((image_width - tile_width) / float(stride) + 2)
    else:
        xtiles = math.ceil((image_width - tile_width) / float(stride) + 1)

    if tile_height != stride:
        ytiles = math.ceil((image_height - tile_height) / float(stride) + 2)
    else:
        ytiles = math.ceil((image_height - tile_height) / float(stride) + 1)

    ytile = 0

    while ytile < ytiles:
        y_start = ytile * stride
        y_end = y_start + window_height
        if y_end > image_height:
            y_start = image_height - window_height
            y_end = y_start + window_height

        ytile += 1
        xtile = 0
        while xtile < xtiles:
            x_start = xtile * stride
            x_end = x_start + window_width
            if x_end > image_width:
                x_start = image_width - window_width
                x_end = x_start + window_width

            xtile += 1

            window = Window(x_start, y_start, window_width, window_height)
            yield window


if __name__ == "__main__":
    pass
