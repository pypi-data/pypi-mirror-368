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

##
## Based on https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/l1c_optimized/
##


import numpy as np

maxR = 3.0
midR = 0.13
sat = 1.3
gamma = 2.3

gOff = 0.01
gOffPow = gOff**gamma
gOffRange = (1 + gOff) ** gamma - gOffPow


class Ray:
    r = 0.013
    g = 0.024
    b = 0.041


def adjGamma(b):
    rez = ((b + gOff) ** gamma - gOffPow) / gOffRange
    return rez


def sAdj(a):
    rez = adjGamma(adj(a, midR, 1, maxR))
    return rez


def clip(d):
    kwargs = {}
    return d.clip(0, 1)


# Saturation enhancement
def satEnh(r, g, b):
    avgS = (r + g + b) / 3.0 * (1 - sat)
    rez = [clip(avgS + r * sat), clip(avgS + g * sat), clip(avgS + b * sat)]
    return rez


# contrast enhancement with highlight compression
def adj(a, tx, ty, maxC):
    ar = clip(a / maxC)
    return (
        ar * (ar * (tx / maxC + ty - 1) - ty) / (ar * (2 * tx / maxC - 1) - tx / maxC)
    )


def sRGB(s):
    lt = s <= 0.0031308
    r = np.where(lt, 12.92 * s, 1.055 * s**0.41666666666 - 0.055)
    return r


def create_tci(red: np.ndarray, green: np.ndarray, blue: np.ndarray, byte=False):
    rgbLin = satEnh(sAdj(red - Ray.r), sAdj(green - Ray.g), sAdj(blue - Ray.b))
    RGB_channels = [sRGB(rgbLin[0]), sRGB(rgbLin[1]), sRGB(rgbLin[2])]
    rgb = np.stack(RGB_channels, axis=-1)
    if byte:
        rgb = 255.0 * rgb
        rgb = rgb.astype(np.uint8)
    return rgb
