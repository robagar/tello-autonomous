from transformers import pipeline

from .fonts import small_font

object_detector = pipeline("object-detection", model="facebook/detr-resnet-50", device="mps")


def detect_objects(frame, draw):
    predictions = object_detector(frame)    

    for p in predictions:
        label = p["label"]
        score = p["score"]
        box = p["box"]
        xmin = box["xmin"]
        xmax = box["xmax"]
        ymin = box["ymin"]
        ymax = box["ymax"]

        draw.rectangle([(xmin, ymin), (xmax, ymax)], outline="yellow")
        draw.text((xmin, ymin-2), f"{label} {score:0.2f}", anchor="lb", fill="blue", font=small_font)
