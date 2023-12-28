#!/usr/bin/env python3

from pathlib import Path
import asyncio
import av
from PIL import Image  
from transformers import pipeline

from tello_asyncio import Tello



# initialize depth detection
depth_estimator = pipeline("depth-estimation", model="vinvino02/glpn-nyu")
DEPTH_HEIGHT = 5
DEPTH_WIDTH = 7
DEPTH_CENTER_I = 2
DEPTH_CENTER_J = 3


# initialize video handling
Path("images").mkdir(exist_ok=True)

codec = av.CodecContext.create('h264', 'r')

current_frame = None

def on_video_frame(drone, buf):
    global current_frame

    try:
        packets = codec.parse(buf)
        for packet in packets:
            frames = codec.decode(packet)
            for frame in frames:
                current_frame = frame # only want the most recent frame

    except Exception as e:
        print(e)
        current_frame = None


async def main():
    drone = Tello()
    try:
        await drone.wifi_wait_for_network(prompt=True)
        await drone.connect()
        await drone.start_video(on_video_frame)
        await drone.takeoff()

        fly = True
        while fly:
            fly = await move(drone)

        await drone.land()
    finally:
        await drone.stop_video()
        await drone.disconnect()

async def move(drone):

    depth = sense_depth()
    if depth:
        center_depth = depth[DEPTH_CENTER_J][DEPTH_CENTER_I]
        print('center depth', center_depth)
        if center_depth > 75:
            print('FORWARD')
            await drone.move_forward(50)
            return True
        else:
            print('STOP')
            return False



f = 0
def sense_depth():
    global f
    if current_frame:
        image = current_frame.to_image()
        image.save(f'images/frame_{f}.jpeg')

        predictions = depth_estimator(image)
        depth_image = predictions["depth"]
        depth_image.save(f'images/depth_{f}.jpeg')

        w = DEPTH_WIDTH
        h = DEPTH_HEIGHT
        depth_image = depth_image.resize((w,h)).convert('L')
        depth_image.save(f'images/depth_{f}_{w}x{h}.png')

        depth = []
        for j in range(h):
            ds = []
            for i in range(w):
                d = depth_image.getpixel((i,j))
                ds.append(d)
            depth.append(ds)

        f += 1

        return depth

asyncio.run(main())
