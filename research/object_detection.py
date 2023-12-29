#!/usr/bin/env python3

from PIL import Image, ImageDraw
from transformers import pipeline
from time import time

object_detector = pipeline("object-detection", model="facebook/detr-resnet-50", device="mps")

N = 9
for i in range(N):
    image = Image.open(f"frames/{i}.jpeg")

    t0 = time()
    predictions = object_detector(image)
    dt = time() - t0
    print(f'took {dt:0.3f}s')

    # print(predictions)

    draw = ImageDraw.Draw(image)
    for p in predictions:
        label = p["label"]
        score = p["score"]
        box = p["box"]
        xmin = box["xmin"]
        xmax = box["xmax"]
        ymin = box["ymin"]
        ymax = box["ymax"]

        draw.rectangle([(xmin, ymin), (xmax, ymax)], outline="yellow")
        draw.text((xmin, ymin-2), f"{label} {score:0.2f}", anchor="lb", fill="blue")

    image.show()

