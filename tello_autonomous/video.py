import asyncio
import av

# TODO measure fov
HORIZONTAL_HALF_FOV = 28.5

codec = av.CodecContext.create('h264', 'r')

current_frame = None

async def init_video(drone, output_dir):
    frame_available = asyncio.Condition()

    await drone.start_video()

    loop = asyncio.get_running_loop()
    loop.create_task(decode_video(drone, frame_available))

    i = 0
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    async def next_frame():
        global current_frame
        nonlocal i
        async with frame_available:
            await frame_available.wait()
            print(f"FRAME {i}")
            i += 1
            image = current_frame.to_image()
            def save_frame_image():
                image.save(frames_dir / f"{i}.jpeg")
            return i, image, save_frame_image

    return next_frame



# def on_video_frame(drone, buf):
#     global current_frame

#     try:
#         packets = codec.parse(buf)
#         for packet in packets:
#             frames = codec.decode(packet)
#             for frame in frames:
#                 current_frame = frame # only want the most recent frame

#     except Exception as e:
#         print(e)
#         current_frame = None


async def decode_video(drone, frame_available):
    global current_frame
    async for buf in drone.video_stream:
        try:
            packets = codec.parse(buf)
            for packet in packets:
                frames = codec.decode(packet)
                for frame in frames:
                    # print("FRAME", frame)
                    async with frame_available:
                        current_frame = frame
                        # print("notify", current_frame)
                        frame_available.notify()

        except Exception as e:
            print(e)
            current_frame = None
