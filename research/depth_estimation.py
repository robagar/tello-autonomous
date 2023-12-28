#!/usr/bin/env python3

from pathlib import Path
from PIL import Image  
from transformers import pipeline
from time import time
import torch
import numpy as np

print('torch.backends.mps.is_available', torch.backends.mps.is_available())
print('torch.backends.mps.is_built', torch.backends.mps.is_built())

base_output_path = Path("output")
base_output_path.mkdir(exist_ok=True)


N = 9

images_960x720 = [None] * N
images_640x480 = [None] * N
images_320x240 = [None] * N
images_160x120 = [None] * N

for i in range(N):
    image_960x720 = Image.open(f"frames/{i}.jpeg")
    images_960x720[i] = image_960x720
    images_640x480[i] = image_960x720.resize((640,480))
    images_320x240[i] = image_960x720.resize((320,240))
    images_160x120[i] = image_960x720.resize((160,120))

def time_depth_estimation(label, depth_estimator, images, i):
    image = images[i]
    w = image.size[0]
    h = image.size[1]

    t0 = time()

    predictions = depth_estimator(image)

    dt = time() - t0
    print(f'{label} {w}x{h} {i}: {dt:0.3f}s')

    return (w, h, predictions)

def do_depth_estimation(label, depth_estimator, images, i):

    (w, h, predictions) = time_depth_estimation(label, depth_estimator, images, i)

    output_path = base_output_path / label / f"{w}x{h}"
    output_path.mkdir(parents=True, exist_ok=True)

    depth_image = predictions["depth"]

    depth_images_path = output_path /  "depth_images"
    depth_images_path.mkdir(exist_ok=True)
    depth_image.save(depth_images_path / f'{i}.jpeg')

    depth_tensor = predictions["predicted_depth"].numpy()
    depth_tensors_path = output_path /  "depth_tensors"
    depth_tensors_path.mkdir(exist_ok=True)
    np.save(depth_tensors_path / f'{i}.npy', depth_tensor)


    # process_depth(i, depth_tensor, output_path)

def process_depth(image_index, depth_tensor, output_path):
    # depth_tensor = depth_tensor[:, 50:,:] 

    (_, h, w) = depth_tensor.shape

    # i = int(w/2)
    # j = int(h/2)
    # d = depth_tensor[0,j,i]
    # print(f'depth at {i},{j}: {d:0.2f}m')

    min_depth = depth_tensor.min()

    max_depth = depth_tensor.max()
    print(f'range: {min_depth:0.3f}-{max_depth:0.3f}m')

    # image = Image.new('L', (w,h))
    # for j in range(h):
    #     for i in range(w):
    #         d = depth_tensor[0,j,i]
    #         l = int(255 * d/max_depth)
    #         image.putpixel((i,j), l) 

    # image.save(output_path / f"normalized_{w}x{h}_{image_index}.png")

    image = Image.new('RGB', (w,h))
    for j in range(h):
        for i in range(w):
            d = depth_tensor[0,j,i]
            if d < 1:
                c = (255,0,0)
            elif d < 2:
                c = (255,127,0)
            elif d < 3:
                c = (255,255,0)
            elif d < 4:
                c = (0,255,0)
            elif d < 5:
                c = (0,255,255)
            else:
                c = (0,0,255)    
            image.putpixel((i,j), c) 

    p = output_path / "colorized"
    p.mkdir(exist_ok=True)
    image.save(p / f"{image_index}.png")

    t = int(h/10)
    b = int(h/2)
    horiz = depth_tensor[:, t:b, :]
    s = int(w / 5)
    ds = []
    for i in range(0, w, s):
        box = horiz[:, :, i:i+s]
        d = box.min()
        ds.append(d)

    print('horizontal depths:', ds) 



def run(label, depth_estimator):
    for i in range(N):
        do_depth_estimation(label, depth_estimator, images_960x720, i)
    # for i in range(N):
    #     do_depth_estimation(label, depth_estimator, images_640x480, i)
    # for i in range(N):
    #     do_depth_estimation(label, depth_estimator, images_320x240, i)
    # for i in range(N):
    #     do_depth_estimation(label, depth_estimator, images_160x120, i)

# https://huggingface.co/vinvino02/glpn-nyu
# run('glpn_nyu', pipeline("depth-estimation", model="vinvino02/glpn-nyu"))
# run('glpn_nyu_mps', pipeline("depth-estimation", model="vinvino02/glpn-nyu", device="mps"))

# run('intel_dpt_large', pipeline("depth-estimation", model="Intel/dpt-large", device='mps'))

# https://huggingface.co/Intel/dpt-hybrid-midas
run('intel_dpt_hybrid_midas', pipeline("depth-estimation", model="Intel/dpt-hybrid-midas", device='mps'))

# bingxin_marigold = pipeline("depth-estimation", model="Bingxin/Marigold", device='mps')
# run('bingxin_marigold', bingxin_marigold)
