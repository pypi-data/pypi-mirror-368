def merge_vids(vids, output_name):
    video = cv2.VideoWriter(output_name, cv2.VideoWriter_fourcc(*"MPEG"), fps, resolution)


    for v in vids:
        curr_v = cv2.VideoCapture(v)
        while curr_v.isOpened():
            r, frame = curr_v.read()
            if not r:
                break 
            video.write(frame)

    video.release()






def split_vids(vid, output_name, intervals):
    pass





if __name__ != "__main__":
    import cv2 
