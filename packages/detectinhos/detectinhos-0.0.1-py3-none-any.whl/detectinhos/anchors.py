from itertools import product
from math import ceil

import torch


def anchors(
    min_sizes: list[list[int]],
    steps: list[int],
    clip: bool,
    resolution: tuple[int, int],  # h, w resolution
) -> torch.Tensor:
    feature_maps = [
        [ceil(resolution[0] / step), ceil(resolution[1] / step)]
        for step in steps
    ]

    anchors: list[float] = []
    for k, f in enumerate(feature_maps):
        t_min_sizes = min_sizes[k]
        for i, j in product(range(f[0]), range(f[1])):
            for min_size in t_min_sizes:
                s_kx = min_size / resolution[1]
                s_ky = min_size / resolution[0]
                dense_cx = [x * steps[k] / resolution[1] for x in [j + 0.5]]
                dense_cy = [y * steps[k] / resolution[0] for y in [i + 0.5]]
                for cy, cx in product(dense_cy, dense_cx):
                    anchors += [cx, cy, s_kx, s_ky]

    # back to torch land
    output = torch.Tensor(anchors).view(-1, 4)
    if clip:
        output.clamp_(max=1, min=0)
    return output
