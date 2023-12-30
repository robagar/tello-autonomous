from PIL import ImageDraw
from time import time

from .depth_perception import deepest_depth, depth_ahead 
from .video import HORIZONTAL_HALF_FOV
from .object_detection import detect_objects
from .fonts import large_font, small_font

STOP_DISTANCE = 1.0
MOVE_DISTANCE = 0.5


async def fly(drone, next_frame, output_dir):
    t0 = time()
    try:
        keep_flying = True
        while keep_flying:

            # wait for next video frame
            frame_index, frame, save_frame = await next_frame()
            draw = ImageDraw.Draw(frame)

            # frame time since start
            t = time() - t0
            draw.text((0,0), f"t={t:0.2f}s", anchor="lt", fill="gray", font=small_font)

            # anything interesting in view?
            detect_objects(frame, draw)

            # decide what to do
            action, description = choose_action(drone, frame_index, frame, draw)

            # add action description
            print(description)
            draw.text((0, frame.height), description, anchor="lb", fill="darkblue", font=large_font)

            # save frame with any annotation
            save_frame()

            if action:
                # do chosen action
                await action
            else:
                keep_flying = False

    finally:    
        if drone.flying:
            print("LAND")
            await drone.land()

        i, frame, save_frame = await next_frame()
        save_frame()

def choose_action(drone, frame_index, frame, draw):
        # first action? take off
        if frame_index == 0:
            return drone.takeoff(), "TAKEOFF"

        # can move forward?
        depth = depth_ahead(frame, draw)
        if depth > STOP_DISTANCE:
            d = MOVE_DISTANCE
            return drone.move_forward(d * 100), f"FORWARDS {d:0.3f}m"      

        # ...no, can see open space to aim for?
        depth, normalized_x = deepest_depth(frame, draw)
        if depth > STOP_DISTANCE:
            angle = normalized_x * HORIZONTAL_HALF_FOV
            return drone.turn_clockwise(angle), f"TURN TOWARDS OPEN SPACE {angle:0.0f}°"
        
        # ...no, look around
        return drone.turn_clockwise(45), "looking around..."
