import asyncio
from pathlib import Path

from tello_asyncio import Tello

from .video import init_video, current_frame
from .fly import fly

output_dir = Path("output")
output_dir.mkdir(exist_ok = True)

async def main():
    print("Tello Autonomous")
    print("================")

    drone = Tello()
    try:
        await drone.wifi_wait_for_network(prompt=True)
        await drone.connect()

        next_frame = await init_video(drone, output_dir)

        # current_frame = await get_current_frame()
        # image = current_frame.to_image()
        # image.save(output_dir / "frame.jpeg")

        await fly(drone, next_frame, output_dir)

    except KeyboardInterrupt:
        pass

    finally:
        await drone.stop_video()
        await drone.disconnect()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass

