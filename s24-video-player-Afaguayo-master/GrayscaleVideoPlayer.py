import threading
import cv2

BUFFER_SIZE = 10           # frames each queue can hold at once
FRAME_DELAY_MS = 42        # ~24 fps, the clip's original frame rate


class FrameQueue:
    """Bounded producer/consumer buffer built only from semaphores and a mutex.

    empty counts free slots and full counts filled slots, so put() blocks
    while the buffer is full and get() blocks while it is empty. The mutex
    guards the list itself. The lab forbids Python's synchronized queues,
    which is why this is written by hand.
    """

    def __init__(self, capacity=BUFFER_SIZE):
        self.items = []
        self.mutex = threading.Lock()                   # binary semaphore
        self.empty = threading.Semaphore(capacity)      # free slots
        self.full = threading.Semaphore(0)              # filled slots

    def put(self, item, stop=None):
        # Wait for a free slot, giving up if the viewer quit early.
        while not self.empty.acquire(timeout=0.1):
            if stop is not None and stop.is_set():
                return False
        with self.mutex:
            self.items.append(item)
        self.full.release()
        return True

    def get(self, stop=None):
        # Wait for a filled slot, giving up if the viewer quit early.
        while not self.full.acquire(timeout=0.1):
            if stop is not None and stop.is_set():
                return None
        with self.mutex:
            item = self.items.pop(0)
        self.empty.release()
        return item


def extractFrames(fileName, outputBuffer, stop):
    count = 0
    vidcap = cv2.VideoCapture(fileName)            # open video file
    success, image = vidcap.read()                 # read first frame

    while success and not stop.is_set():
        print(f'Reading frame {count}')
        if not outputBuffer.put(image, stop):      # blocks while the buffer is full
            break
        success, image = vidcap.read()
        count += 1

    vidcap.release()
    print('Frame extraction complete')
    outputBuffer.put(None, stop)                   # end of frames


def colorToGrayscale(coloredBuffer, grayscaleBuffer, stop):
    count = 0
    while True:
        frame = coloredBuffer.get(stop)            # blocks while the buffer is empty
        if frame is None:                          # end of frames (or viewer quit)
            break
        print(f'Converting frame {count}')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if not grayscaleBuffer.put(gray, stop):
            break
        count += 1
    print('Grayscale conversion complete')
    grayscaleBuffer.put(None, stop)                # end of frames


def displayFrames(inputBuffer, stop):
    count = 0
    while True:
        frame = inputBuffer.get(stop)
        if frame is None:
            break
        print(f'Displaying frame {count}')
        cv2.imshow('Video', frame)
        # waitKey returns the key code; mask it to compare with 'q'
        if cv2.waitKey(FRAME_DELAY_MS) & 0xFF == ord('q'):
            stop.set()                             # tell the other threads to stop
            break
        count += 1
    print('Finished displaying all frames')
    cv2.destroyAllWindows()


def main(filename='clip.mp4'):
    coloredFrames = FrameQueue()                   # extract -> grayscale
    grayscaleFrames = FrameQueue()                 # grayscale -> display
    stop = threading.Event()                       # set when the viewer presses q

    workers = [
        threading.Thread(target=extractFrames, args=(filename, coloredFrames, stop)),
        threading.Thread(target=colorToGrayscale, args=(coloredFrames, grayscaleFrames, stop)),
        threading.Thread(target=displayFrames, args=(grayscaleFrames, stop)),
    ]
    for worker in workers:                         # all three run concurrently
        worker.start()
    for worker in workers:
        worker.join()


if __name__ == '__main__':
    main()
