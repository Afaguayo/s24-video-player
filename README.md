# Producer–Consumer Video Player

A three-stage video pipeline in Python, where every stage runs on its own thread: one thread **extracts** frames from `clip.mp4`, one **converts** them to grayscale, and one **displays** them at the clip's original 24 fps. The threads pass frames through bounded buffers that I built from counting semaphores and a mutex, which is the point of the lab. Python's own thread-safe queues weren't allowed.

Spring 2024 operating systems lab: producer–consumer with semaphores. The original assignment is in [`s24-video-player-Afaguayo-master/README.md`](s24-video-player-Afaguayo-master/README.md).

## Run it

```bash
pip install opencv-python
cd s24-video-player-Afaguayo-master
python3 GrayscaleVideoPlayer.py      # press q in the video window to stop early
```

## How it works

```text
clip.mp4 ─▶ [extract] ─▶ FrameQueue(10) ─▶ [grayscale] ─▶ FrameQueue(10) ─▶ [display @ 24 fps]
             thread 1                        thread 2                         thread 3
```

`FrameQueue` in [`GrayscaleVideoPlayer.py`](s24-video-player-Afaguayo-master/GrayscaleVideoPlayer.py) is the classic bounded buffer:

- `empty`, a counting semaphore starting at 10, counts free slots. `put()` waits on it, so a producer blocks while the buffer is full.
- `full`, a counting semaphore starting at 0, counts frames waiting. `get()` waits on it, so a consumer blocks while the buffer is empty.
- A mutex guards the list itself while a frame is added or removed.

Each stage sends `None` when it's done, so the next stage knows to finish, and every frame is processed exactly once. Pressing **q** sets a shared stop flag that the waiting threads check, so all three exit cleanly instead of blocking forever.

**Checked:** all 739 frames of the clip come through once, in order and in grayscale; neither buffer ever holds more than 10 frames; quitting early leaves no threads running.

## Files

| File | What it is |
|---|---|
| `GrayscaleVideoPlayer.py` | **The lab solution:** a three-thread extract → grayscale → display pipeline |
| `ColoredVideoPlayer.py` | Earlier step: two threads, extract → display, in color |
| `ExtractFrames.py`, `ConvertToGrayscale.py`, `DisplayFrames.py`, `ExtractAndDisplay.py` | Single-threaded starter scripts from the assignment |
