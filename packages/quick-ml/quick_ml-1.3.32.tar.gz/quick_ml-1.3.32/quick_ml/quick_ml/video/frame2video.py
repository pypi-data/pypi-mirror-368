def convt_frames2vid(pathIn, pathOut, fps):

    frame_array = []

    files = [f for f in os.listdir(pathIn) if os.path.isfile(os.path.join(pathIn, f))]

    files.sort(key = lambda x: int(x[5:-4]))

    for i in range(len(files)):
        filename = pathIn + files[i]

        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width, height)
        print(filename)
        frame_array.append(img)

    out = cv2.VideoWriter(pathOut, cv2.VideoWriter_fourcc(*"DIVX"), fps, size)

    for i in range(len(frame_array)):
        out.write(frame_array[i])

    out.release()





if __name__ != "__main__":
    import cv2 
    import numpy as np 
    import os