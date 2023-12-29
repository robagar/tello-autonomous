from transformers import pipeline
import numpy as np

# https://huggingface.co/vinvino02/glpn-nyu
depth_estimator = pipeline("depth-estimation", model="vinvino02/glpn-nyu")

def perceive_depths(frame):
    results = depth_estimator(frame)
    depths_tensor = results["predicted_depth"].numpy()
    return depths_tensor

def horizontal_min_depths(frame):
    depths = perceive_depths(frame)
    (_,h,w) = depths.shape
    t = int(h/10)
    b = int(h/2)
    ds = depths[:, t:b, :]
    return ds.min(1)[0]  

def deepest_depth(frame, draw):
    ds = horizontal_min_depths(frame)
    (w,) = ds.shape
    
    indices = np.array(range(w))
    x = np.average(indices, weights=ds)
    depth = ds[int(x)]
    
    hw = w/2
    normalized_x = (x - hw) / hw

    if draw:
        y0 = frame.height / 10
        y1 = frame.height / 2
        draw.line([(x,y0), (x, y1)], "green")
        draw.text((x,y0), f"{depth:0.3f}m", fill="green", anchor="ms")

    return depth, normalized_x     

def depth_ahead(frame, draw=None):
    ds = horizontal_min_depths(frame)
    (w,) = ds.shape
    
    # sample box in center of frame
    c = int(w/2)
    b = int(w/20)
    l = c - b
    r = c + b
    depth = ds[l:r].min()

    if draw:
        # draw sampled box
        x0 = frame.width * l/w
        y0 = frame.height / 10
        x1 = frame.width * r/w
        y1 = frame.height / 2
        draw.rectangle([(x0, y0), (x1, y1)], "blue")

        # draw min depth value in box
        x = (x0 + x1) / 2
        y = (y0 + y1) / 2
        draw.text((x,y), f"{depth:0.3f}m", fill="blue", anchor="ms")

    return depth

