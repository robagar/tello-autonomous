#!/usr/bin/env python3

from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

label = "glpn_nyu"
# label = "intel_dpt_hybrid_midas"

output_path = Path("output") / label / "960x720"

N = 1

def show_depths(depths):
    (_,h,w) = depths.shape
    m = depths.max()

    image = Image.new('L', (w,h))
    for j in range(h):
        for i in range(w):
            d = depths[0,j,i]
            l = int(255 * d/m)
            image.putpixel((i,j), l)

    image.show() 

for i in range(N):
    depths = np.load(output_path / "depth_tensors" / f"{i}.npy")
    print(depths.shape)

    show_depths(depths)
     
    (_,h,w) = depths.shape
    # print(f"all depths {w}x{h}")

    t = int(h/10)
    b = int(h/2)

    using_depths = depths[:, t:b, :]
    (_,h,w) = using_depths.shape
    # print(f"using depths {w}x{h}")

    horizontal_min_depths = using_depths.min(1)[0]
    # print(horizontal_min_depths[0].shape)

    indices = np.array(range(w))
    # print(indices.shape)

    target_x = np.average(indices, weights=horizontal_min_depths)
    print(f'target_x: {target_x:0.3f}')

    target_depth = horizontal_min_depths[int(target_x)]
    print(f"target depth: {target_depth:0.3f}m")

    image = Image.open(f"frames/{i}.jpeg")

    draw = ImageDraw.Draw(image)
    draw.line([(target_x, t), (target_x, b)], fill="blue") 

    image.show()


