from PIL import ImageDraw

from .depth_perception import deepest_depth, depth_ahead 
from .video import HORIZONTAL_HALF_FOV
from .object_detection import detect_objects

STOP_DISTANCE = 1.0
MOVE_DISTANCE = 0.5

async def fly(drone, next_frame, output_dir):
    print("waiting for video...")
    i, frame, save_frame = await next_frame()
    save_frame()

    print("TAKEOFF")
    action = drone.takeoff()

    try:
        while action:
            # do chosen action
            await action

            # wait for next video frame
            i, frame, save_frame = await next_frame()
            draw = ImageDraw.Draw(frame)

            # anything interesting in view?
            detect_objects(frame, draw)

            # decide what to do
            action = choose_action(drone, frame, draw)

            # save frame with any annotation
            save_frame()

    finally:    
        if drone.flying:
            print("LAND")
            await drone.land()

        i, frame, save_frame = await next_frame()
        save_frame()

def choose_action(drone, frame, draw):
        # can move forward?
        depth = depth_ahead(frame, draw)
        if depth > STOP_DISTANCE:
            d = MOVE_DISTANCE
            print(f"FORWARDS {d:0.3f}m")
            return drone.move_forward(d * 100)      

        # ...no, can see open space to aim for?
        depth, normalized_x = deepest_depth(frame, draw)
        if depth > STOP_DISTANCE:
            angle = normalized_x * HORIZONTAL_HALF_FOV
            print(f"TURN TOWARDS OPEN SPACE{angle:0.1f}°")
            return drone.turn_clockwise(angle)
        
        # ...no, look around
        print("looking around...")
        return drone.turn_clockwise(45)
