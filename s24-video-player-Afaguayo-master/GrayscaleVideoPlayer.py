import threading
import cv2
import numpy as np
import base64
import queue



def extractFrames(fileName, outputBuffer, maxFramesToLoad=9999):
    # Initialize frame count 
    count = 0

    # open video file
    vidcap = cv2.VideoCapture(fileName)

    # read first image
    success,image = vidcap.read()
    
    print(f'Reading frame {count} {success}')
    while success and count < maxFramesToLoad:
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)

        if not success:
            break

        #encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)

        # add the frame to the buffer
        outputBuffer.put(image)
        success,image = vidcap.read()
        print(f'Reading frame {count} {success}')
        count += 1

    print('Frame extraction complete')
    outputBuffer.put(None)      # End of frame


def displayFrames(inputBuffer):
    # initialize frame count
    count = 0

    # go through each frame in the buffer until the buffer is empty
    while True:
        # get the next frame
        frame = inputBuffer.get()

        if frame is None:
            break

        print(f'Displaying frame {count}')        

        # display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        cv2.imshow('Video', frame)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

        count += 1


    print('Finished displaying all frames')
    # cleanup the windows
    cv2.destroyAllWindows()

def colorToGrayscale(coloredBuffer, GrayscaleBuffer):
    # initialize frame count
    count = 0

    # go through each frame in the buffer until the buffer is empty
    while True:
        frame = coloredBuffer.get()                                 # Get the next frame

        if frame is None:                                           # If no frames break
            break

        print(f'Displaying frame {count}')        

        frames = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)            # Convert to grayscale

        GrayscaleBuffer.put(frames)                                 # Put in new queue
        

        count += 1
    GrayscaleBuffer.put(None)                                       # End of frames



filename = 'clip.mp4'                                              # filename of clip to load

coloredFramesQueue = queue.Queue()                                 # Holds colored frames to play
grayscaleFramesQueue = queue.Queue()                               # Holds gray frames to play

# Create thread to run Extracting frames in parallel
extractWorker = threading.Thread(target=extractFrames, args=(filename,coloredFramesQueue,10))
extractWorker.start()

# Create thread to run color to grayscale function in parallel
grayscaleWorker = threading.Thread(target=colorToGrayscale,args=(coloredFramesQueue,grayscaleFramesQueue))
grayscaleWorker.start()

# Create thread to run display frames in parallel 
displayWorker = threading.Thread(target=displayFrames,args=(grayscaleFramesQueue,))
displayWorker.start()

# Join all created threads to main thread
extractWorker.join()
grayscaleWorker.join()
displayWorker.join()

