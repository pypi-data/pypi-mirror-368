class V2F():

    def __init__(self, output_folder):
        self.output_folder = output_folder


    @staticmethod
    def fetch_from_url(self, url, destination_folder):
        pass

    def __get_fps(self, video_file):
        video = cv2.VideoCapture(video_file);

        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

        if int(major_ver)  < 3 :
            fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
            print ("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))
        else:
            fps = video.get(cv2.CAP_PROP_FPS)
            print ("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))

        video.release()
        return int(round(fps))

    def __video_duration(self, filename):

        video = cv2.VideoCapture(filename)

        duration = video.get(cv2.CAP_PROP_POS_MSEC)
        frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)

        return duration, frame_count

    """
    def convert_multiVids_2frames(self, video_paths, video_names, sparsify = True, frame_freqs = None, multiprocessing = True):
        assert isinstance(video_paths, list)
        assert len(video_paths) > 1
        if sparsify:
            assert frame_freq is not None

        if multiprocessing:
            #p1 = 
            pass

        else:
            if frame_freq is None:
                pass


            elif frame_freq == 'same':
                pass


            for i in range(len(video_paths)):
                self.convert2frames(video_paths[i], video_names[i], sparsify, frame_freq)
    """



    def convert2frames(self, video_path, video_name, sparsify = True, frame_freq = None):
        assert os.path.isfile(video_path) == True
        
        if sparsify:
            #frame_freq = int(input("Please enter the save frequency for frames per second: \n"))
            assert frame_freq is not None 
            assert isinstance(frame_freq, int)

        cam = cv2.VideoCapture(video_path)

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder) 

        currentframe = 0
        min_time_counter = 1
        frame_counter = 0
        fps = self.__get_fps(video_path)
        intervals = random.sample(range(0, fps), frame_freq)
        random_intervals = []

        min_intervals = []
        for i in range(0, 60):
            for j in intervals:
                min_intervals.append(j + (fps*i))

        while(True):

            ret, frame = cam.read()

            if ret:
                frame_counter += 1

                name = f'{self.output_folder}/{video_name}/{str(min_time_counter)}/frame' + str(currentframe) + '.jpg'
                #print ('Creating...' + name)
                if not os.path.exists(self.output_folder + '/' + video_name + '/' + str(min_time_counter)):
                    os.makedirs(self.output_folder + '/' + video_name + '/' + str(min_time_counter))
  
                # writing the extracted images
                if sparsify == "yes" :
        
        
        
                    #if frame_counter % 60 == 0:
        
                    #if divisible(frame_counter, random_intervals):
                    #if frame_counter in random_intervals:
                    if frame_counter in min_intervals:
            
                        cv2.imwrite(name, frame)
                        print ('Creating...' + name)
                else:
                    cv2.imwrite(name, frame)
                    print ('Creating...' + name)


                # increasing counter so that it will
                # show how many frames are created
                currentframe += 1

                if frame_counter >= fps * 60:
                    #start_time = time.time()
                    min_time_counter += 1
                    frame_counter = 0

            else:
                break

        cam.release()
        cv2.destroyAllWindows()


    def extract_interval(self, start, end, video_path, video_name, sparsify = True, frame_freq = None):
        assert len(start) == 8
        assert len(end) == 8
        assert (start[2] == ":") and (start[5] == ":")
        assert int((datetime.strptime(end, "%H:%M:%S") - datetime.strptime(start, "%H:%M:%S")).total_seconds()) > 0
        if sparsify:
            assert frame_freq is not None 
            assert isinstance(frame_freq, int)


        start_sec = int((datetime.strptime(start, "%H:%M:%S") - datetime(1900,1,1)).total_seconds())
        end_sec = int((datetime.strptime(end, "%H:%M:%S") - datetime(1900,1,1)).total_seconds())



        cam = cv2.VideoCapture(video_path)

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder) 

        currentframe = 0
        min_time_counter = 0
        frame_counter = 0
        fps = self.__get_fps(video_path)

        start_frame = start_sec * fps 
        end_frame = end_sec * fps 

        print("Starting From -> ", start_frame)
        print("Ending At -> ", end_frame)

        print("FPS -> ", fps)
        print("Frame freq -> ", frame_freq)
        print(self.__video_duration(video_path))
        if sparsify:
            intervals = random.sample(range(0, fps), frame_freq)
        
            random_intervals = []

            min_intervals = []
            for i in range(0, 60):
                for j in intervals:
                    min_intervals.append(j + (fps*i))

        while(True):

            ret, frame = cam.read()

            if ret:
                currentframe += 1
                frame_counter += 1

                name = f'{self.output_folder}/{video_name}/{str(min_time_counter)}/frame' + str(currentframe) + '.jpg'

                if not os.path.exists(self.output_folder + '/' + video_name + '/' + str(min_time_counter)):
                    os.makedirs(self.output_folder + '/' + video_name + '/' + str(min_time_counter))


                if (currentframe >= start_frame) and (currentframe <= end_frame):
                                   
                    if sparsify:
                        if frame_counter in min_intervals:
           
                            cv2.imwrite(name, frame)
                            print ('Creating...' + name) 
                    else:
                        cv2.imwrite(name, frame)
                        print ('Creating...' + name)
                        
                elif currentframe > end_frame :
                    break 
                
                
                if frame_counter >= fps * 60:
                  #start_time = time.time()
                    min_time_counter += 1
                    frame_counter = 0

            
            else:
              break


        # while(True):

        #     ret, frame = cam.read()

        #     if ret:
                

        #         frame_counter += 1

        #         name = f'{self.output_folder}/{video_name}/{str(min_time_counter)}/frame' + str(currentframe) + '.jpg'
        #         #print ('Creating...' + name)
        #         if not os.path.exists(self.output_folder + '/' + video_name + '/' + str(min_time_counter)):
        #             os.makedirs(self.output_folder + '/' + video_name + '/' + str(min_time_counter))
  
                


        #         # writing the extracted images
                

        #         if sparsify == "yes" :
        
        
        
        #             if frame_counter in min_intervals:
           
        #                 cv2.imwrite(name, frame)
        #                 print ('Creating...' + name)
                

        #         else:
        #             cv2.imwrite(name, frame)
        #             print ('Creating...' + name)


        #         # increasing counter so that it will
        #         # show how many frames are created
        #         currentframe += 1

        #         if frame_counter >= fps * 60:
        #           #start_time = time.time()
        #             min_time_counter += 1
        #             frame_counter = 0

        #     else:
        #         break

        cam.release()
        cv2.destroyAllWindows()



    def extract_multi_intervals(self, intervals_starts, intervals_ends, video_path, video_name, sparsify = True, frame_freq = None):
        """
        In Making...
        """
        
        pass


        # assert len(intervals_starts) == len(intervals_ends)
        # assert len(intervals_starts) > 1

        # for i in zip(intervals_starts, intervals_ends):
        #     self.extract_interval(i[0], i[1], video_path, video_name, sparsify, frame_freq)
        #     print(f"Completed {i[0]} to {i[1]}")

        # print("Done!")
    

    def compress(self, output_file_name):

        zipf = zipfile.ZipFile(output_file_name, 'w', zipfile.ZIP_DEFLATED)
        self.__zipdir(self.output_folder, zipf)
        zipf.close()


    def __zipdir(self, path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file), 
                           os.path.relpath(os.path.join(root, file), 
                                           os.path.join(path, '..')))



if __name__ != "__main__":
    import os
    import cv2 
    import numpy as np 
    from tqdm import tqdm 
    from glob import glob
    import random
    import zipfile

    from datetime import datetime
    from multiprocessing import Process
    
      
